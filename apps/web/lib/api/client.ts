import { translate as tr, localizeMessage } from '../translations';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
let connection: Promise<string> | undefined;
export async function origin() {
  if (!connection)
    connection = window.desktop
      ? window.desktop.connection().then((c) => c.origin)
      : Promise.resolve(window.location.origin);
  return connection;
}
async function request(path: string, method = 'GET', body?: unknown): Promise<Response> {
  const token = sessionStorage.getItem('on-token');
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
  if (body && !(body instanceof FormData)) headers['Content-Type'] = 'application/json';
  const response = await fetch((await origin()) + '/api' + path, {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  }).catch(() => {
    throw new Error(tr('error.network'));
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      typeof error.detail === 'string'
        ? localizeMessage(error.detail)
        : response.status === 422
          ? tr('error.validation')
          : tr('error.request', { status: response.status }),
      response.status,
    );
  }
  return response;
}
export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  return (await request(path, method, body)).json();
}
export async function apiBlob(path: string): Promise<Blob> {
  return (await request(path)).blob();
}
export async function apiEmpty(path: string, method: string): Promise<void> {
  await request(path, method);
}
