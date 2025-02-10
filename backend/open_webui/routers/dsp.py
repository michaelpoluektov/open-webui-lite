import asyncio
import json
import copy
import io
import logging
import traceback
import wave
import zipfile
from typing import Optional, TypedDict

import audio_dsp.stages
import numpy as np
from audio_dsp.design.parse_json import DspJson, Graph, insert_forks, make_pipeline
from audio_dsp.design.pipeline import Pipeline
from audio_dsp.models.stage import all_models
from fastapi import APIRouter, Depends, File, Query, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from open_webui.utils.auth import get_verified_user
from open_webui.models.dsp_sessions import DspSessions, DspSessionModel

log = logging.getLogger(__name__)

router = APIRouter()

graph_update_subscriptions: dict[str, list[asyncio.Queue]] = {}


def notify_graph_update(session_id: str, user_id: str):
    if session_id in graph_update_subscriptions:
        session = DspSessions.get_session(session_id, user_id=user_id)
        if session is None:
            return
        data = session.graph
        for queue in graph_update_subscriptions[session_id]:
            queue.put_nowait(data)


@router.get("/schema/graph")
def get_dsp_json_schema(_=Depends(get_verified_user)):
    schema = copy.deepcopy(Graph.model_json_schema())
    return JSONResponse(schema)


@router.get("/schema/params")
def get_params_schema(_=Depends(get_verified_user)):
    params = {
        k: n.model_fields["parameters"].annotation.model_json_schema()
        for k, n in all_models().items()
        if (
            hasattr(n.model_fields, "parameters")
            and hasattr(n.model_fields["parameters"].annotation, "model_json_schema")
        )
    }
    return JSONResponse(params)


@router.post("/session/{session_id}")
def create_session(session_id: str, user=Depends(get_verified_user)) -> DspSessionModel:
    """Create a new DSP session."""
    if DspSessions.get_session(session_id, user.id):
        raise HTTPException(status_code=409, detail="Session already exists")
    return DspSessions.create_session(session_id, user.id)


@router.get("/session/{session_id}")
def get_session(session_id: str, user=Depends(get_verified_user)) -> DspSessionModel:
    """Get a DSP session by ID."""
    session = DspSessions.get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions")
def list_sessions(user=Depends(get_verified_user)) -> list[DspSessionModel]:
    """List all DSP sessions for the current user."""
    return DspSessions.get_user_sessions(user.id)


@router.delete("/session/{session_id}")
def delete_session(session_id: str, user=Depends(get_verified_user)):
    """Delete a DSP session."""
    if not DspSessions.delete_session(session_id, user.id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}


@router.post("/graph/params")
def set_parameters(params: dict, session_id: str, user=Depends(get_verified_user)):
    session = DspSessions.get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = Graph.model_validate(session.graph)
    for node in graph.nodes:
        if node.placement.name in params and hasattr(node, "parameters"):
            node.parameters = node.parameters.__class__(**params[node.placement.name])

    forked_graph = insert_forks(graph)
    make_pipeline(
        DspJson(ir_version=1, producer_name="test", producer_version="0.1", graph=graph)
    )

    # Update session with new graphs
    session = DspSessions.update_session(
        session_id, user.id, graph.model_dump(), forked_graph.model_dump()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    notify_graph_update(session_id, user.id)
    return {"message": "Parameters successfully set."}


def parse_wav_bytes(file_bytes: bytes):
    with wave.open(io.BytesIO(file_bytes), "rb") as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        raw_data = wav_file.readframes(n_frames)
    return raw_data, n_channels, sample_width, sample_rate, n_frames


def bytes_to_array(raw_data: bytes, sample_width: int, n_channels: int):
    if sample_width == 2:
        dtype = np.int16
    elif sample_width == 4:
        dtype = np.int32
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported sample width: {sample_width}"
        )
    data = np.frombuffer(raw_data, dtype=dtype).reshape(-1, n_channels)
    return data


def adjust_channels(data: np.ndarray, current_channels: int, desired_channels: int):
    if desired_channels == current_channels:
        return data
    if desired_channels == 2 and current_channels == 1:
        return np.column_stack((data, data))
    elif desired_channels == 1 and current_channels == 2:
        return data.mean(axis=1, keepdims=True).astype(data.dtype)
    raise HTTPException(status_code=400, detail="Unsupported channel conversion")


def normalize_audio(data: np.ndarray, sample_width: int):
    max_value = float(2 ** (8 * sample_width - 1))
    return data.astype(np.float32) / max_value


def array_to_wav_bytes(data: np.ndarray, sample_rate: int):
    scaled_data = (data * 32767.0).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(data.shape[1])
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(scaled_data.tobytes())
    buffer.seek(0)
    return buffer.getvalue()


@router.post("/graph/audio")
async def run_audio(
    session_id: str = Query(...),
    files: list[UploadFile] = File(...),
    user=Depends(get_verified_user),
):
    session = DspSessions.get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = Graph.model_validate(session.graph)
    forked_graph = Graph.model_validate(session.forked_graph)

    pipeline = make_pipeline(
        DspJson(ir_version=1, producer_name="test", producer_version="0.1", graph=graph)
    )

    if not hasattr(graph, "inputs"):
        raise HTTPException(status_code=400, detail="Graph inputs not defined.")

    expected_input_count = len(graph.inputs)
    if len(files) != expected_input_count:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {expected_input_count} input files, but got {len(files)}.",
        )

    audio_segments = []
    sample_rates = []
    frame_counts = []
    common_sample_width = None

    for file, input_def in zip(files, graph.inputs):
        file_bytes = await file.read()
        raw_data, n_channels, sample_width, sample_rate, n_frames = parse_wav_bytes(
            file_bytes
        )
        sample_rates.append(sample_rate)
        frame_counts.append(n_frames)
        desired_channels = len(input_def.output)
        data = bytes_to_array(raw_data, sample_width, n_channels)
        data = adjust_channels(data, n_channels, desired_channels)
        data = normalize_audio(data, sample_width)
        audio_segments.append(data)
        if common_sample_width is None:
            common_sample_width = sample_width
        elif common_sample_width != sample_width:
            raise HTTPException(
                status_code=400, detail="All files must have the same sample width."
            )

    if len(set(sample_rates)) != 1:
        raise HTTPException(
            status_code=400, detail="All files must have the same sample rate."
        )

    min_frames = min(frame_counts)
    audio_segments = [seg[:min_frames, :] for seg in audio_segments]
    combined_audio = np.hstack(audio_segments)
    executor = pipeline.executor().process
    result = executor(combined_audio)
    processed_audio = result.data
    output_sample_rate = int(result.fs)

    output_files = {}
    out_channel_idx = 0
    for output_def in forked_graph.outputs:
        num_channels = len(output_def.input)
        out_data = processed_audio[
            :min_frames, out_channel_idx : out_channel_idx + num_channels
        ]
        out_channel_idx += num_channels
        wav_bytes = array_to_wav_bytes(out_data, output_sample_rate)
        output_files[output_def.name] = wav_bytes

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for out_name, wav_bytes in output_files.items():
            zip_file.writestr(f"{out_name}.wav", wav_bytes)
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=outputs.zip"},
    )


@router.post("/graph")
def set_graph(graph: Graph, session_id: str, user=Depends(get_verified_user)):
    try:
        forked_graph = insert_forks(graph)

        # validate
        make_pipeline(
            DspJson(
                ir_version=1, producer_name="test", producer_version="0.1", graph=graph
            )
        )

        # Update session with new graphs
        session = DspSessions.update_session(
            session_id, user.id, graph.model_dump(), forked_graph.model_dump()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        notify_graph_update(session_id, user.id)

        schema_dict = {
            node.placement.name: node.parameters.__class__.model_json_schema()
            for node in forked_graph.nodes
            if hasattr(node, "parameters")
        }
        return schema_dict
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "traceback": traceback.format_exc()},
            status_code=400,
        )


@router.get("/graph")
def get_graph(session_id: str, user=Depends(get_verified_user)):
    session = DspSessions.get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return Graph.model_validate(session.graph)


@router.get("/graph-updates")
async def graph_updates(session_id: str, user=Depends(get_verified_user)):
    # Verify session exists and belongs to user
    session = DspSessions.get_session(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    queue = asyncio.Queue()
    if session_id not in graph_update_subscriptions:
        graph_update_subscriptions[session_id] = []
    graph_update_subscriptions[session_id].append(queue)

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            graph_update_subscriptions[session_id].remove(queue)
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")
