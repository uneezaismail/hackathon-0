/**
 * Ralph Wiggum Stop Hook - Gold Tier AI Employee
 *
 * Intercepts Claude Code exit attempts and checks if task is complete.
 * Completion strategies:
 * 1. File-movement: Task file moved from Needs_Action/ to Done/
 * 2. Promise-based: Output contains <promise>TASK_COMPLETE</promise>
 *
 * Returns:
 * - { allowExit: true } - Task complete, allow exit
 * - { allowExit: false, injectPrompt: "..." } - Task incomplete, continue loop
 */

const fs = require('fs');
const path = require('path');

module.exports = async function stopHook(context) {
  const STATE_FILE = path.join(process.cwd(), '.claude', 'ralph-loop.local.md');
  const VAULT_DIR = path.join(process.cwd(), 'My_AI_Employee', 'AI_Employee_Vault');
  const NEEDS_ACTION_DIR = path.join(VAULT_DIR, 'Needs_Action');
  const DONE_DIR = path.join(VAULT_DIR, 'Done');
  const LOG_FILE = path.join(VAULT_DIR, 'Logs', 'ralph-loop.log');
  const HISTORY_DIR = path.join(VAULT_DIR, 'Ralph_History');

  // Check if Ralph Loop is active
  if (!fs.existsSync(STATE_FILE)) {
    return { allowExit: true };
  }

  // Parse state file (YAML frontmatter + Markdown body)
  const stateContent = fs.readFileSync(STATE_FILE, 'utf8');
  const frontmatterMatch = stateContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);

  if (!frontmatterMatch) {
    log(LOG_FILE, 'ERROR: Invalid state file format');
    return { allowExit: true };
  }

  const frontmatter = parseFrontmatter(frontmatterMatch[1]);
  const prompt = frontmatterMatch[2].trim();

  const iteration = parseInt(frontmatter.iteration || '0');
  const maxIterations = parseInt(frontmatter.max_iterations || '10');
  const watchFile = frontmatter.watch_file;
  const completionPromise = frontmatter.completion_promise;

  log(LOG_FILE, `Ralph Wiggum Stop Hook - Checking completion (iteration ${iteration}/${maxIterations})`);

  // Check max iterations
  if (iteration >= maxIterations) {
    log(LOG_FILE, `✅ Max iterations reached (${iteration}/${maxIterations})`);
    archiveState(STATE_FILE, HISTORY_DIR);
    return {
      allowExit: true,
      message: `Ralph Loop completed: Max iterations reached (${iteration}/${maxIterations})`
    };
  }

  // Check file-movement completion
  if (watchFile) {
    const filename = path.basename(watchFile);
    const doneFilePath = path.join(DONE_DIR, filename);

    if (fs.existsSync(doneFilePath)) {
      log(LOG_FILE, `✅ File-movement completion: ${filename} found in Done/`);
      archiveState(STATE_FILE, HISTORY_DIR);
      return {
        allowExit: true,
        message: `Ralph Loop completed: Task file moved to Done/ (${iteration} iterations)`
      };
    }

    // Check if file no longer in Needs_Action
    if (!fs.existsSync(watchFile)) {
      log(LOG_FILE, `✅ File-movement completion: ${filename} no longer in Needs_Action/`);
      archiveState(STATE_FILE, HISTORY_DIR);
      return {
        allowExit: true,
        message: `Ralph Loop completed: Task file processed (${iteration} iterations)`
      };
    }
  }

  // Check promise-based completion
  if (completionPromise && context.output) {
    const promiseTag = `<promise>${completionPromise}</promise>`;
    if (context.output.includes(promiseTag)) {
      log(LOG_FILE, `✅ Promise completion: ${promiseTag} detected`);
      archiveState(STATE_FILE, HISTORY_DIR);
      return {
        allowExit: true,
        message: `Ralph Loop completed: Promise detected (${iteration} iterations)`
      };
    }
  }

  // Task incomplete - continue loop
  log(LOG_FILE, `🔄 Task incomplete - continuing to iteration ${iteration + 1}/${maxIterations}`);

  // Increment iteration
  const newIteration = iteration + 1;
  const updatedFrontmatter = frontmatterMatch[1]
    .replace(/iteration: \d+/, `iteration: ${newIteration}`)
    .replace(/last_iteration_at: .*/, `last_iteration_at: "${new Date().toISOString()}"`);

  const updatedState = `---\n${updatedFrontmatter}\n---\n${prompt}`;
  fs.writeFileSync(STATE_FILE, updatedState, 'utf8');

  return {
    allowExit: false,
    injectPrompt: prompt,
    message: `Ralph Loop continuing: iteration ${newIteration}/${maxIterations}`
  };
};

// Helper functions
function parseFrontmatter(yaml) {
  const result = {};
  yaml.split('\n').forEach(line => {
    const match = line.match(/^(\w+):\s*(.+)$/);
    if (match) {
      result[match[1]] = match[2].replace(/^["']|["']$/g, '');
    }
  });
  return result;
}

function log(logFile, message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;

  try {
    const logDir = path.dirname(logFile);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    fs.appendFileSync(logFile, logMessage, 'utf8');
  } catch (err) {
    console.error('Failed to write log:', err);
  }
}

function archiveState(stateFile, historyDir) {
  try {
    if (!fs.existsSync(historyDir)) {
      fs.mkdirSync(historyDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const archiveFile = path.join(historyDir, `ralph-loop_${timestamp}.md`);

    fs.renameSync(stateFile, archiveFile);
    log(path.join(path.dirname(historyDir), 'Logs', 'ralph-loop.log'),
        `State archived to: ${archiveFile}`);
  } catch (err) {
    console.error('Failed to archive state:', err);
  }
}
