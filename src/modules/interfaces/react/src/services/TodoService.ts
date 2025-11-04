/**
 * TodoService
 * 
 * Integration service for the To-Do Desktop Assistant.
 * Bridges the React CLI with the Python To-Do automation system.
 * Emits events for task creation, execution, and status updates.
 */

import { spawn, ChildProcess } from 'node:child_process';
import { EventEmitter } from 'node:events';
import path from 'node:path';
import { loggingService } from './LoggingService.js';

export interface TodoTask {
  id: number;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  actions: Array<{
    tool: string;
    params: Record<string, any>;
    description?: string;
  }>;
  created_at: string;
  updated_at: string;
  result?: any;
  error?: string;
}

export interface TodoServiceEvents {
  'task:created': (task: TodoTask) => void;
  'task:executing': (taskId: number) => void;
  'task:completed': (taskId: number, result: any) => void;
  'task:failed': (taskId: number, error: string) => void;
  'action:log': (log: any) => void;
  'vision:mode:changed': (enabled: boolean) => void;
}

export class TodoService extends EventEmitter {
  private pythonProcess?: ChildProcess;
  private projectRoot: string;
  private visionModeEnabled: boolean = false;

  constructor() {
    super();
    // Find project root
    this.projectRoot = process.env.CYBER_PROJECT_ROOT || process.cwd();
    loggingService.info('TodoService initialized', { projectRoot: this.projectRoot });
  }

  /**
   * Add a new to-do task
   */
  async addTask(description: string): Promise<TodoTask> {
    loggingService.info('Adding to-do task', { description });

    try {
      const result = await this.executePython('add_task', { description });
      
      if (result.success && result.task) {
        const task: TodoTask = result.task;
        this.emit('task:created', task);
        loggingService.info('Task created', { taskId: task.id, actions: task.actions.length });
        return task;
      } else {
        throw new Error(result.error || 'Failed to add task');
      }
    } catch (error) {
      loggingService.error('Failed to add task', { error });
      throw error;
    }
  }

  /**
   * Execute a task (with optional dry-run)
   */
  async executeTask(taskId: number, dryRun: boolean = false): Promise<any> {
    loggingService.info('Executing task', { taskId, dryRun });
    
    this.emit('task:executing', taskId);

    try {
      const result = await this.executePython('execute_task', { 
        task_id: taskId, 
        dry_run: dryRun 
      });

      if (result.success) {
        this.emit('task:completed', taskId, result);
        loggingService.info('Task completed', { taskId, dryRun });
        return result;
      } else {
        this.emit('task:failed', taskId, result.error || 'Unknown error');
        loggingService.error('Task execution failed', { taskId, error: result.error });
        throw new Error(result.error || 'Task execution failed');
      }
    } catch (error) {
      this.emit('task:failed', taskId, String(error));
      loggingService.error('Task execution error', { taskId, error });
      throw error;
    }
  }

  /**
   * List all tasks
   */
  async listTasks(status?: string): Promise<TodoTask[]> {
    loggingService.info('Listing tasks', { status });

    try {
      const result = await this.executePython('list_tasks', { status });
      
      if (result.success && result.tasks) {
        return result.tasks;
      } else {
        throw new Error(result.error || 'Failed to list tasks');
      }
    } catch (error) {
      loggingService.error('Failed to list tasks', { error });
      throw error;
    }
  }

  /**
   * Get task details
   */
  async getTask(taskId: number): Promise<TodoTask | null> {
    loggingService.info('Getting task', { taskId });

    try {
      const result = await this.executePython('get_task', { task_id: taskId });
      
      if (result.success && result.task) {
        return result.task;
      } else if (result.task === null) {
        return null;
      } else {
        throw new Error(result.error || 'Failed to get task');
      }
    } catch (error) {
      loggingService.error('Failed to get task', { taskId, error });
      throw error;
    }
  }

  /**
   * Cancel a task
   */
  async cancelTask(taskId: number): Promise<boolean> {
    loggingService.info('Cancelling task', { taskId });

    try {
      const result = await this.executePython('cancel_task', { task_id: taskId });
      
      if (result.success) {
        loggingService.info('Task cancelled', { taskId });
        return true;
      } else {
        throw new Error(result.error || 'Failed to cancel task');
      }
    } catch (error) {
      loggingService.error('Failed to cancel task', { taskId, error });
      throw error;
    }
  }

  /**
   * Enable/disable vision mode
   */
  async setVisionMode(enabled: boolean): Promise<void> {
    loggingService.info('Setting vision mode', { enabled });

    try {
      const result = await this.executePython('set_vision_mode', { enabled });
      
      if (result.success) {
        this.visionModeEnabled = enabled;
        this.emit('vision:mode:changed', enabled);
        loggingService.info('Vision mode changed', { enabled });
      } else {
        throw new Error(result.error || 'Failed to set vision mode');
      }
    } catch (error) {
      loggingService.error('Failed to set vision mode', { enabled, error });
      throw error;
    }
  }

  /**
   * Get action logs
   */
  async getActionLogs(): Promise<any[]> {
    try {
      const result = await this.executePython('get_action_logs', {});
      
      if (result.success && result.logs) {
        return result.logs;
      } else {
        return [];
      }
    } catch (error) {
      loggingService.error('Failed to get action logs', { error });
      return [];
    }
  }

  /**
   * Get automation info
   */
  async getAutomationInfo(): Promise<any> {
    try {
      const result = await this.executePython('get_automation_info', {});
      
      if (result.success && result.info) {
        return result.info;
      } else {
        throw new Error(result.error || 'Failed to get automation info');
      }
    } catch (error) {
      loggingService.error('Failed to get automation info', { error });
      throw error;
    }
  }

  /**
   * Get deployment information
   */
  async getDeploymentInfo(): Promise<any> {
    try {
      const result = await this.executePython('get_deployment_info', {});
      
      if (result.success && result.deployment) {
        return result.deployment;
      } else {
        throw new Error(result.error || 'Failed to get deployment info');
      }
    } catch (error) {
      loggingService.error('Failed to get deployment info', { error });
      throw error;
    }
  }

  /**
   * Execute Python command via subprocess
   */
  private async executePython(command: string, params: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(
        this.projectRoot,
        'src',
        'modules',
        'todo_assistant',
        'cli_bridge.py'
      );

      const args = [
        scriptPath,
        command,
        JSON.stringify(params)
      ];

      loggingService.debug('Executing Python command', { command, scriptPath });

      const process = spawn('python3', args, {
        cwd: this.projectRoot,
        env: { ...process.env, PYTHONPATH: path.join(this.projectRoot, 'src') }
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        loggingService.debug('Python stderr', { stderr: data.toString() });
      });

      process.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (error) {
            loggingService.error('Failed to parse Python output', { stdout, error });
            reject(new Error(`Failed to parse output: ${stdout}`));
          }
        } else {
          loggingService.error('Python process failed', { code, stderr });
          reject(new Error(`Python process exited with code ${code}: ${stderr}`));
        }
      });

      process.on('error', (error) => {
        loggingService.error('Failed to spawn Python process', { error });
        reject(error);
      });
    });
  }

  /**
   * Clean up resources
   */
  dispose(): void {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = undefined;
    }
    this.removeAllListeners();
    loggingService.info('TodoService disposed');
  }
}

// Singleton instance
let todoServiceInstance: TodoService | null = null;

export function getTodoService(): TodoService {
  if (!todoServiceInstance) {
    todoServiceInstance = new TodoService();
  }
  return todoServiceInstance;
}
