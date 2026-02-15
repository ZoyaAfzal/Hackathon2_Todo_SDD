/**
 * Task entity types for the frontend.
 *
 * These types match the API response schemas from api-contract.md.
 */

/**
 * Task entity returned from the API.
 */
export interface Task {
  id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
  version: number
}

/**
 * Data for creating a new task.
 */
export interface TaskCreate {
  title: string
  description?: string
}

/**
 * Data for updating an existing task.
 * All fields except version are optional.
 */
export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
  version: number
}

/**
 * Request body for complete/uncomplete operations.
 */
export interface VersionRequest {
  version: number
}

/**
 * Response from list tasks endpoint.
 */
export interface TaskListResponse {
  tasks: Task[]
  has_more: boolean
  next_cursor: string | null
}
