#!/usr/bin/env node
import { formatResult, isJson, runInstaller } from './index.js';

const result = runInstaller();
process.stdout.write(isJson(process.argv.slice(2)) ? `${JSON.stringify(result, null, 2)}\n` : `${formatResult(result)}\n`);
process.exit(1);
