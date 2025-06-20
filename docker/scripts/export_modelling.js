#!/usr/bin/env node
/**
 * Export Modelling (MDL) from WrenAI
 * 
 * This script exports the complete modelling definition from WrenAI system:
 * - Models, columns, relationships, views
 * - Export to JSON file in /app/data/
 */

const fs = require('fs');
const path = require('path');

// Configuration
const UI_GRAPHQL_ENDPOINT = "http://localhost:3000/api/graphql";
const OUTPUT_DIR = "/app/data";

// Use dynamic import for fetch
async function loadFetch() {
  const { default: fetch } = await import('node-fetch');
  return fetch;
}

function getCurrentTimestamp() {
  const now = new Date();
  return now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

async function getLatestDeployHash() {
  // For now, return the known hash
  // This should be enhanced to query the database or add GraphQL query
  return "852c9584f33bf6df0006a983b332dfa524282eeb";
}

async function queryMDL(hashValue) {
  const fetch = await loadFetch();
  
  const query = `
    query GetMDL {
      getMDL(hash: "${hashValue}") {
        hash
        mdl
      }
    }
  `;
  
  const payload = {
    query: query
  };
  
  try {
    const response = await fetch(UI_GRAPHQL_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    if (response.ok) {
      const result = await response.json();
      if (result.errors) {
        console.log(`❌ GraphQL Error: ${JSON.stringify(result.errors)}`);
        return null;
      } else {
        return result.data.getMDL;
      }
    } else {
      console.log(`❌ HTTP Error: ${response.status} - ${await response.text()}`);
      return null;
    }
  } catch (error) {
    console.log(`❌ Request Error: ${error.message}`);
    return null;
  }
}

function decodeMDL(encodedMDL) {
  try {
    const decodedStr = Buffer.from(encodedMDL, 'base64').toString('utf-8');
    return JSON.parse(decodedStr);
  } catch (error) {
    console.log(`❌ Error decoding MDL: ${error.message}`);
    return null;
  }
}

function exportMDLToJSON(mdlData, outputPath) {
  if (!mdlData) {
    console.log("⚠️  No MDL data to export");
    return false;
  }
  
  try {
    fs.writeFileSync(outputPath, JSON.stringify(mdlData, null, 2), 'utf-8');
    
    // Print summary
    const modelsCount = mdlData.models ? mdlData.models.length : 0;
    const relationshipsCount = mdlData.relationships ? mdlData.relationships.length : 0;
    const viewsCount = mdlData.views ? mdlData.views.length : 0;
    
    console.log(`✅ Successfully exported MDL to ${outputPath}`);
    console.log(`   📊 Models: ${modelsCount}`);
    console.log(`   🔗 Relationships: ${relationshipsCount}`);
    console.log(`   👁️  Views: ${viewsCount}`);
    console.log(`   🗄️  DataSource: ${mdlData.dataSource || 'Unknown'}`);
    console.log(`   🏷️  Catalog: ${mdlData.catalog || 'Unknown'}`);
    console.log(`   📋 Schema: ${mdlData.schema || 'Unknown'}`);
    
    return true;
  } catch (error) {
    console.log(`❌ Error exporting MDL: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('=' .repeat(80));
  console.log('📤 WrenAI Modelling (MDL) Export Tool');
  console.log('=' .repeat(80));
  console.log(`⏰ Export time: ${new Date().toISOString()}`);
  console.log();
  
  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
  
  // Get latest deployment hash
  console.log("🔍 Getting latest deployment hash...");
  const hashValue = await getLatestDeployHash();
  console.log(`   Hash: ${hashValue}`);
  console.log();
  
  // Export MDL
  console.log("📋 Exporting MDL...");
  const mdlResult = await queryMDL(hashValue);
  
  if (mdlResult !== null) {
    // Decode the base64 encoded MDL
    console.log("🔓 Decoding MDL...");
    const mdlData = decodeMDL(mdlResult.mdl);
    
    if (mdlData) {
      // Export to JSON file
      const timestamp = getCurrentTimestamp();
      const mdlFile = path.join(OUTPUT_DIR, `modelling_export_${timestamp}.json`);
      
      if (exportMDLToJSON(mdlData, mdlFile)) {
        console.log();
        console.log("✅ MDL export completed successfully!");
        console.log(`📁 File saved: ${mdlFile}`);
      } else {
        console.log("❌ Failed to export MDL");
        process.exit(1);
      }
    } else {
      console.log("❌ Failed to decode MDL");
      process.exit(1);
    }
  } else {
    console.log("❌ Failed to query MDL");
    process.exit(1);
  }
  
  console.log();
  console.log("🎉 Export process completed!");
}

// Install node-fetch if not available
async function ensureDependencies() {
  try {
    require.resolve('node-fetch');
  } catch (e) {
    console.log("📦 Installing node-fetch...");
    const { execSync } = require('child_process');
    execSync('npm install node-fetch@2', { stdio: 'inherit' });
  }
}

if (require.main === module) {
  ensureDependencies().then(() => {
    main().catch(error => {
      console.error('❌ Unexpected error:', error);
      process.exit(1);
    });
  });
} 