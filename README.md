# Divya Jain — Python Portfolio

A production-minded personal portfolio built with Flask, semantic HTML, modern CSS, vanilla JavaScript, and SQLite. The project was created for a Python programming assignment while keeping the frontend polished enough to use as a real personal website.

The presentation includes three selected product projects, a categorized technical-skills matrix, a branded loading sequence, scroll reveals, animated metrics and marquee text, rotating focus copy, pointer-responsive depth effects, and a reduced-motion fallback.

## What makes it a Python project

- Flask renders the portfolio and project data on the server.
- `GET /api/profile` returns live JSON used by the interactive terminal.
- `POST /api/contact` validates submissions, checks CSRF tokens, rate-limits requests, and stores production messages in private Vercel Blob storage.
- `GET /health` provides a small deployment health check.
- Pytest covers rendering, API behavior, persistence, validation, and security headers.

## Run locally

On Windows, double-click `RUN_ME.bat`. It creates the virtual environment when needed, installs missing packages, starts the Flask server, and opens the portfolio in your browser.

For manual setup, use:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

If Windows does not provide the `py` command, use your installed Python 3.11+ executable in the first command.

## Configuration

Copy `.env.example` values into your shell or hosting provider. The application reads environment variables directly.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Long random value used to protect the Flask session. Required in production. |
| `LINKEDIN_URL` | Full LinkedIn profile URL. The LinkedIn link stays hidden when this is empty. |
| `APP_ENV` | Set to `production` to enable secure session cookies behind HTTPS. |
| `PORT` | Web server port. Defaults to `5000`. |

PowerShell example:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-value"
$env:LINKEDIN_URL = "https://www.linkedin.com/in/your-profile/"
python app.py
```

## Deploy on Vercel

1. Push this repository to GitHub.
2. Open [vercel.com/new](https://vercel.com/new) and import the `Portfolio` repository.
3. Keep the detected framework and build settings unchanged; Vercel detects the root `app.py` Flask application automatically.
4. Add a long random `SECRET_KEY` environment variable. Optionally add `LINKEDIN_URL`.
5. Set `APP_ENV` to `production`, then deploy.

The production project uses a private Vercel Blob store named `portfolio-messages`. Vercel supplies its storage credentials automatically; do not copy those credentials into the repository.

## Tests

```powershell
python -m pytest -q
```

## Project structure

```text
Portfolio/
├── RUN_ME.bat                One-click Windows setup and launcher
├── app.py                    Flask app, APIs, validation, storage routing, security headers
├── contact_storage.py        Private Vercel Blob message persistence
├── portfolio_data.py         Profile, projects, and technology content
├── templates/
│   ├── index.html            Main server-rendered portfolio
│   └── 404.html              Custom not-found page
├── static/
│   ├── css/style.css         Responsive visual system
│   ├── images/               Profile image and favicon
│   └── js/main.js            Navigation, reveals, API demo, contact form
├── tests/test_app.py         Automated Flask tests
└── requirements.txt
```

## Contact-message note

Local messages are stored in `instance/portfolio.sqlite3`. Production messages are durable private JSON records in Vercel Blob. To view them, open the `portfolio` project in Vercel, select **Storage**, open **portfolio-messages**, and browse the `messages/` folder. Only authenticated members of the Vercel account can access the records.

## Content provenance

The name, public email, bio direction, and selected project details were verified from the `divya-aicodes` GitHub repositories and current local project metadata. Project summaries are based on the repositories' README files. The LinkedIn URL is intentionally configurable because no trustworthy exact profile URL was available in the verified sources.
