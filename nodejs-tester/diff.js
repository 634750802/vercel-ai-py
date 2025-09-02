import fs from 'fs'
import Differ from 'json-diff-kit/dist/differ.js';

const standard = JSON.parse(fs.readFileSync('../standard.json', 'utf-8'))
const result = JSON.parse(fs.readFileSync('../result.json', 'utf-8'))


const differ = new Differ({
  detectCircular: true,    // default `true`
  maxDepth: Infinity,      // default `Infinity`
  showModifications: true, // default `true`
  arrayDiffMethod: 'normal',  // default `"normal"`, but `"lcs"` may be more useful
});

differ.diff(standard, result).forEach(res => {
    res.forEach(r => {
        if (r.type !== 'equal') {
            console.log(`${r.lineNumber}:${r.type}`, r.text)
        }
    })
})