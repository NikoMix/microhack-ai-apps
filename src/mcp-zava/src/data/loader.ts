/**
 * Zava seed-data loader.
 *
 * Reads JSON and Markdown files from DATA_DIR (env var) or the canonical
 * `data/` directory at the repository root (detected at runtime).
 *
 * All data is loaded once at startup and kept in memory — the seed dataset
 * is small (~10 products, ~6 orders, a handful of policy/supplier docs) so
 * in-memory is the right model for this dev/demo server.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// ── Type definitions that mirror data/README.md ──────────────────────────────

export interface Product {
    id: string;
    name: string;
    category: string;
    subcategory: string;
    price: number;
    currency: string;
    sizes: string[];
    colors: string[];
    smartFeatures: string[];
    batteryHours: number;
    washCycles: number;
    description: string;
    inStock: number;
    rating: number;
}

export interface OrderItem {
    productId: string;
    qty: number;
    size: string;
    color: string;
}

export interface Order {
    orderId: string;
    customer: string;
    customerName: string;
    status: string;
    placedOn: string;
    items: OrderItem[];
    total: number;
    shipTo: string;
}

export interface Customer {
    id: string;
    name: string;
    type: string;
    industry: string;
    associationType: string;
    primaryPillars: string[];
    description: string;
}

export interface Review {
    productId: string;
    customer: string;
    rating: number;
    title: string;
    text: string;
}

/** Named document from policies/ or suppliers/ */
export interface KnowledgeDoc {
    /** Source directory: "policies" | "suppliers" */
    source: "policies" | "suppliers";
    /** Filename without extension, e.g. "returns" */
    slug: string;
    /** Full Markdown content */
    content: string;
}

/** The complete in-memory dataset */
export interface ZavaData {
    products: Product[];
    orders: Order[];
    customers: Customer[];
    reviews: Review[];
    knowledge: KnowledgeDoc[];
}

// ── Loader ───────────────────────────────────────────────────────────────────

/**
 * Resolves the data directory.
 *
 * Priority:
 *   1. DATA_DIR environment variable (absolute path — set by Dockerfile / azd)
 *   2. Repository-root `data/` directory detected relative to this file
 *      (works for local dev with `tsx` or compiled `dist/`)
 */
function resolveDataDir(): string {
    if (process.env.DATA_DIR) {
        return resolve(process.env.DATA_DIR);
    }
    // __dirname of compiled dist/data/loader.js is:
    //   .../src/mcp-zava/dist/data
    // go up 4 levels to reach repo root, then into data/
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);
    return resolve(__dirname, "../../../../data");
}

function readJson<T>(filePath: string): T {
    const raw = readFileSync(filePath, "utf-8");
    return JSON.parse(raw) as T;
}

function readMarkdownDir(dirPath: string, source: KnowledgeDoc["source"]): KnowledgeDoc[] {
    try {
        return readdirSync(dirPath)
            .filter((f) => f.endsWith(".md"))
            .map((f) => ({
                source,
                slug: f.replace(/\.md$/, ""),
                content: readFileSync(join(dirPath, f), "utf-8"),
            }));
    } catch {
        // Directory might not exist in minimal deployments — return empty
        return [];
    }
}

/**
 * Loads all Zava seed data from the data directory.
 * Called once at startup by `createZavaServer()`.
 */
export function loadData(): ZavaData {
    const dataDir = resolveDataDir();

    const products = readJson<Product[]>(join(dataDir, "products.json"));
    const orders = readJson<Order[]>(join(dataDir, "orders.json"));
    const customers = readJson<Customer[]>(join(dataDir, "customers.json"));
    const reviews = readJson<Review[]>(join(dataDir, "reviews.json"));
    const knowledge: KnowledgeDoc[] = [
        ...readMarkdownDir(join(dataDir, "policies"), "policies"),
        ...readMarkdownDir(join(dataDir, "suppliers"), "suppliers"),
    ];

    console.error(
        `[zava-mcp] Loaded ${products.length} products, ${orders.length} orders, ` +
        `${customers.length} customers, ${reviews.length} reviews, ` +
        `${knowledge.length} knowledge docs from ${dataDir}`
    );

    return { products, orders, customers, reviews, knowledge };
}
