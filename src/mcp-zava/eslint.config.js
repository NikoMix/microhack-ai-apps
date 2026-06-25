// @ts-check
import js from "@eslint/js";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import globals from "globals";

/** @type {import("eslint").Linter.Config[]} */
export default [
    {
        ignores: ["dist/**", "node_modules/**", "*.mjs"],
    },
    {
        ...js.configs.recommended,
        languageOptions: {
            globals: {
                ...globals.node,
                ...globals.es2022,
            },
        },
    },
    {
        files: ["src/**/*.ts"],
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                project: "./tsconfig.json",
                ecmaVersion: 2022,
                sourceType: "module",
            },
            globals: {
                ...globals.node,
                ...globals.es2022,
            },
        },
        plugins: {
            "@typescript-eslint": tsPlugin,
        },
        rules: {
            ...tsPlugin.configs.recommended.rules,
            "no-undef": "off", // TypeScript handles this
            "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
            "@typescript-eslint/explicit-function-return-type": "off",
            "@typescript-eslint/no-explicit-any": "warn",
        },
    },
];
