// module.exports = {
// 	root: true,
// 	extends: [
// 		'eslint:recommended',
// 		'plugin:@typescript-eslint/recommended',
// 		'plugin:svelte/recommended',
// 		'plugin:cypress/recommended',
// 		'prettier'
// 	],
// 	parser: '@typescript-eslint/parser',
// 	plugins: ['@typescript-eslint'],
// 	parserOptions: {
// 		sourceType: 'module',
// 		ecmaVersion: 2020,
// 		extraFileExtensions: ['.svelte']
// 	},
// 	env: {
// 		browser: true,
// 		es2017: true,
// 		node: true
// 	},
// 	overrides: [
// 		{
// 			files: ['*.svelte'],
// 			parser: 'svelte-eslint-parser',
// 			parserOptions: {
// 				parser: '@typescript-eslint/parser'
// 			}
// 		}
// 	]
// };
module.exports = {
  plugins: ["unused-imports"],
  rules: {
    "unused-imports/no-unused-imports": "error",
    "unused-imports/no-unused-vars": [
      "warn",
      { vars: "all", varsIgnorePattern: "^_", args: "after-used", argsIgnorePattern: "^_" }
    ]
  }
};
