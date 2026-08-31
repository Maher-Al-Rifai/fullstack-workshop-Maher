# Module 11 — Demo Guide: Frontend API Integration and State

---

## 1. Start the full stack

```powershell
# From workspace root
docker compose up --build -d
docker compose ps   # confirm db, backend, frontend are healthy
```

Then open `http://localhost:3000`.

---

## 2. Register a new user

Navigate to `/register`. Fill in name, email, password and submit. Verify in DevTools Network tab:

- `POST /api/v1/auth/register` → 201 with user JSON
- Immediately followed by `POST /api/v1/auth/login` (form-encoded body)
- Response sets an `HttpOnly` cookie named `refresh_token`
- `GET /api/v1/auth/me` uses `Authorization: Bearer <token>` header

After success: page redirects to `/dashboard` and the header shows the user's name with a "Sign out" button.

---

## 3. Test login error handling

From `/login`, enter a wrong password. Show that:
- The error message reads "Invalid email or password." — not the raw backend JSON
- The form stays enabled after the error (can retry)
- No password is logged to the console

---

## 4. Show the in-memory token — no localStorage

Open DevTools → Application → Local Storage. Show it is empty for `localhost:3000`.

Open DevTools → Application → Cookies. Show the `refresh_token` HTTP-only cookie — the browser prevents JavaScript from reading it.

In the console:
```javascript
// This returns null because the token is not in localStorage
localStorage.getItem('access_token')
```

---

## 5. Demonstrate token refresh on hard reload

While logged in, hard-reload the page (Ctrl+Shift+R). Show:
1. The Pinia `auth.accessToken` is gone (in-memory only)
2. The `auth.client.ts` plugin calls `POST /api/v1/auth/refresh` (visible in Network)
3. A new access token is issued using the cookie
4. `GET /api/v1/auth/me` follows with the new Bearer token
5. The user is still shown as authenticated — no login required

---

## 6. Create a project

Navigate to `/projects`. Click "New project". Fill in name, toggle "Make this project public". Submit.

Show in Network tab:
- `POST /api/v1/projects` with the request body
- 201 response with the project JSON
- The new project appears at the top of the list immediately (optimistic insert from the 201 response)

---

## 7. Create tasks and advance status

Click into a project. Click "Add task", enter a title. Show:
- `POST /api/v1/projects/{id}/tasks` → 201 with new task in `backlog`
- Task card appears with "Backlog" badge and "Move to in progress" button

Click "Move to in progress":
- `PATCH /api/v1/projects/{id}/tasks/{taskId}` with `{ "status": "in_progress" }`
- Task card updates to show "In Progress" badge and "Move to done" button

---

## 8. Show conflict error for invalid transition

Try to advance a `done` task (it has no advance button — the button is hidden when `nextStatus` is null). Explain why: `NEXT_STATUS` in `TaskCard.vue` maps only valid forward transitions.

To show the API reject: open the Network tab and manually send:
```
PATCH /api/v1/projects/{id}/tasks/{doneTaskId}
{ "status": "backlog" }
```
→ 409 with `"code": "invalid_transition"`. The `apiFetch` normalizes this to `{ message, status, code }`.

---

## 9. Show the 401 retry in action

With the backend running, corrupt the in-memory token (DevTools console):
```javascript
// Access the Pinia store via Vue devtools or:
const auth = window.__pinia__.state.value.auth
auth.accessToken = 'bad-token'
```

Now navigate to `/projects`. Show in Network:
1. `GET /api/v1/projects` → 401 (bad token)
2. `POST /api/v1/auth/refresh` (cookie sent)
3. `GET /api/v1/projects` retried with new token → 200

---

## 10. Route protection

Open a private tab (no cookie) and navigate directly to `http://localhost:3000/dashboard`. The middleware redirects to `/login?redirect=%2Fdashboard`. After successful login, the return URL is preserved.

Show that `/login` itself redirects authenticated users to `/dashboard` (no loop).

---

## 11. Logout

Click "Sign out" in the header. Show:
- `POST /api/v1/auth/logout` → 204, cookie deleted
- Pinia state cleared: `user = null`, `accessToken = null`
- Redirected to `/`
- `/dashboard` now redirects to `/login` again

---

## 12. Quality gate

```bash
cd frontend
npm run lint       # 0 errors
npm run typecheck  # Type check passed
npm run build      # Build complete
npm test           # vitest — no test files yet, exits 0
```

---

## Summary checklist

- [ ] Register → login → dashboard flow working end to end
- [ ] Access token in Pinia (not localStorage), refresh cookie HTTP-only
- [ ] Hard reload recovers session via refresh endpoint
- [ ] 401 → refresh → retry demonstrated
- [ ] Project create shows in list immediately
- [ ] Task create, advance, delete all work
- [ ] Invalid transition shows normalized error message
- [ ] Route middleware redirects unauthenticated users with return URL
- [ ] Logout clears state and cookies
- [ ] All four quality gates pass
