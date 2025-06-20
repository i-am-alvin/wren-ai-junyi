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
const http = require('http');

// Configuration
const OUTPUT_DIR = "/app/data";
const HASH = "852c9584f33bf6df0006a983b332dfa524282eeb";

function getCurrentTimestamp() {
  const now = new Date();
  return now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

function makeGraphQLRequest(query) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ query });
    
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: '/api/graphql',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.errors) {
            reject(new Error(`GraphQL Error: ${JSON.stringify(result.errors)}`));
          } else {
            resolve(result.data);
          }
        } catch (error) {
          reject(new Error(`Parse Error: ${error.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(new Error(`Request Error: ${error.message}`));
    });
    
    req.write(postData);
    req.end();
  });
}

async function queryMDL(hashValue) {
  const query = `
    query GetMDL {
      getMDL(hash: "${hashValue}") {
        hash
        mdl
      }
    }
  `;
  
  try {
    const result = await makeGraphQLRequest(query);
    return result.getMDL;
  } catch (error) {
    console.log(`❌ ${error.message}`);
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
  
  // Get deployment hash
  console.log("🔍 Using deployment hash...");
  console.log(`   Hash: ${HASH}`);
  console.log();
  
  // Export MDL
  console.log("📋 Exporting MDL...");
  const mdlResult = await queryMDL(HASH);
  
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

if (require.main === module) {
  main().catch(error => {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
  });
} 