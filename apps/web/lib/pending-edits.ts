// Destructive workspace actions must let mounted editors flush first.
const guards = new Map<() => Promise<boolean>, string | undefined>();
export function registerPendingEdits(guard: () => Promise<boolean>, scope?: string) {
  guards.set(guard, scope);
  return () => {
    guards.delete(guard);
  };
}
export async function settlePendingEdits(scope?: string) {
  for (const [guard, owner] of guards) {
    if (scope !== undefined && owner !== scope) continue;
    if (!(await guard())) return false;
  }
  return true;
}
