// One-shot script to dump frontend mock data to JSON for Python backend.
import { SIXSENSE_DATA } from '../frontend/src/mocks/data.js'
import { writeFileSync } from 'node:fs'

writeFileSync('./app/data.json', JSON.stringify(SIXSENSE_DATA, null, 2))
console.log('Wrote ./app/data.json')
console.log('Top-level keys:', Object.keys(SIXSENSE_DATA))
