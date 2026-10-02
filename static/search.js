// Import Transformers.js using an open CDN compatible with GitHub Pages hosting
import { pipeline, cosine_similarity } from 'https://jsdelivr.net';

let extractor;
let buildingsDatabase = [];
let buildingEmbeddings = [];

// 1. Initialize the AI model & load dataset
async function initializeSearchEngine() {
    console.log("Loading semantic extraction model...");
    // Minimal footprint model (~23MB) running completely on the client CPU/GPU
    extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    
    // Fetch your static schema file from root
    const response = await fetch('./buildings.json');
    const data = await response.json();
    buildingsDatabase = data.buildings;

    // Pre-calculate vector targets for every building
    console.log("Vectorizing campus metadata structures...");
    for (const building of buildingsDatabase) {
        // Build a semantic profile combining names, aliases, and granular keywords
        const targetText = `Building: ${building.name}. Shorthand: ${building.aliases.join(', ')}. Contains: ${building.keywords.join(', ')}.`;
        
        // Generate raw embedding tensor
        const output = await extractor(targetText, { pooling: 'mean', normalize: true });
        
        buildingEmbeddings.push({
            id: building.id,
            vector: Array.from(output.data) // Convert Tensor data into standard JS array
        });
    }
    console.log("Search Engine Ready!");
}

// 2. Query execution engine
async function semanticSearch(queryText, matchThreshold = 0.2, limit = 3) {
    if (!extractor) return [];

    // Vectorize user text input string
    const queryOutput = await extractor(queryText, { pooling: 'mean', normalize: true });
    const queryVector = Array.from(queryOutput.data);

    // Compute mathematical similarity across all entries
    const searchResults = buildingsDatabase.map((building, index) => {
        const storedVector = buildingEmbeddings[index].vector;
        const similarityScore = cosine_similarity(queryVector, storedVector);
        
        return {
            building: building,
            score: similarityScore
        };
    });

    // Sort by proximity score and drop records beneath threshold tolerance
    return searchResults
        .filter(result => result.score >= matchThreshold)
        .sort((a, b) => b.score - a.score)
        .slice(0, limit);
}

// Example usage hook
// (Trigger this when someone clicks "Search" or types into your navigation UI input field)
/*
initializeSearchEngine().then(async () => {
    const hits = await semanticSearch("where can I swim or lift weights?");
    console.log("Matches found:", hits);
});
*/
