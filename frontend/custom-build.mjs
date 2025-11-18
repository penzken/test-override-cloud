import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const crmAppPath = path.resolve(__dirname, '../../crm/frontend');
const overrideSrcPath = path.resolve(__dirname, 'src');
const overrideFilesPath = path.resolve(__dirname, './src_overrides');

console.log('Starting: Copying original src from CRM app.');
fs.copySync(path.join(crmAppPath, 'src'), overrideSrcPath);
console.log('Completed: Copying original src.');

console.log('Starting: Overriding src with custom files.');
fs.copySync(overrideFilesPath, overrideSrcPath);
console.log('Completed: Overriding src.');

console.log('Installing dependencies...');
execSync('yarn install', { stdio: 'inherit' });
console.log('Dependencies installed.');

