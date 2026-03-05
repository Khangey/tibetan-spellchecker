/**
 * Tibetan Spellchecker - Netlify Serverless Function
 * 基于 tibetan-spellchecker 词典资源
 */
const fs = require('fs');
const path = require('path');

const TSHEG = '\u0f0b';
const SHAD = '\u0f0d';

function loadDictionary(baseDir) {
  const valid = new Set();
  const syllablesDir = path.join(baseDir, 'syllables');

  const suffixes = JSON.parse(
    fs.readFileSync(path.join(syllablesDir, 'suffixes.json'), 'utf8')
  );
  suffixes.NB = [''];

  function loadRootTxt(filePath) {
    fs.readFileSync(filePath, 'utf8')
      .split('\n')
      .forEach((line) => {
        line = line.trim();
        if (!line || line.startsWith('#')) return;
        if (line.includes('/')) {
          const [root, suffixType] = line.split('/', 2).map((s) => s.trim());
          if (suffixes[suffixType]) {
            suffixes[suffixType].forEach((suf) => valid.add(root + suf));
          }
        }
      });
  }

  function loadWithSuffixes(filePath) {
    if (!fs.existsSync(filePath)) return;
    fs.readFileSync(filePath, 'utf8')
      .split('\n')
      .forEach((line) => {
        line = line.trim();
        if (!line) return;
        if (line.includes('/')) {
          const [root, suffixType] = line.split('/', 2).map((s) => s.trim());
          if (suffixes[suffixType]) {
            suffixes[suffixType].forEach((suf) => valid.add(root + suf));
          }
        } else {
          valid.add(line);
        }
      });
  }

  function loadPlain(filePath) {
    if (!fs.existsSync(filePath)) return;
    fs.readFileSync(filePath, 'utf8')
      .split('\n')
      .forEach((line) => {
        line = line.trim();
        if (line) valid.add(line);
      });
  }

  loadRootTxt(path.join(syllablesDir, 'root.txt'));
  loadWithSuffixes(path.join(syllablesDir, 'wasurs.txt'));
  loadWithSuffixes(path.join(syllablesDir, 'rare.txt'));
  loadPlain(path.join(syllablesDir, 'exceptions.txt'));
  loadWithSuffixes(path.join(syllablesDir, 'proper-names.txt'));

  // supplement.txt - 补充词典
  const supplementPath = path.join(syllablesDir, 'supplement.txt');
  if (fs.existsSync(supplementPath)) {
    fs.readFileSync(supplementPath, 'utf8')
      .split('\n')
      .forEach((line) => {
        line = line.trim();
        if (line && !line.startsWith('#')) valid.add(line);
      });
  }

  return valid;
}

function spellcheckText(text, validSyllables) {
  const result = [];
  let start = 0;

  for (let i = 0; i <= text.length; i++) {
    if (i === text.length || text[i] === TSHEG) {
      if (i > start) {
        const syl = text.slice(start, i);
        if (syl && !/^\s+$/.test(syl)) {
          const hasTibetan = /[\u0f00-\u0fff]/.test(syl);
          if (hasTibetan) {
            const lookup = syl.replace(new RegExp(SHAD + '+$'), '');
            result.push({
              syllable: syl,
              start,
              end: i,
              valid: validSyllables.has(lookup),
            });
          }
        }
      }
      start = i + 1;
    }
  }
  if (start < text.length) {
    const syl = text.slice(start);
    if (syl && !/^\s+$/.test(syl) && /[\u0f00-\u0fff]/.test(syl)) {
      const lookup = syl.replace(new RegExp(SHAD + '+$'), '');
      result.push({
        syllable: syl,
        start,
        end: text.length,
        valid: validSyllables.has(lookup),
      });
    }
  }

  return result;
}

// 词典在首次调用时加载并缓存
let validSyllables = null;

function getDictionary() {
  if (!validSyllables) {
    // Netlify 打包后 included_files 会在项目根目录，使用 process.cwd()
    const baseDir = process.cwd();
    validSyllables = loadDictionary(baseDir);
  }
  return validSyllables;
}

exports.handler = async (event, context) => {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ detail: 'Method not allowed' }),
    };
  }

  try {
    const body = JSON.parse(event.body || '{}');
    const text = body.text || '';

    const dict = getDictionary();
    const results = spellcheckText(text, dict);
    const errorCount = results.filter((r) => !r.valid).length;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        results,
        text,
        error_count: errorCount,
      }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ detail: err.message }),
    };
  }
};
