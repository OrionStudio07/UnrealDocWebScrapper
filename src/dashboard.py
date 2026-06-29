import http.server
import json
import socketserver
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PORT = 8000
VAULT_DIR = PROJECT_ROOT / "UE5_Obsidian_Vault"
META_DIR = VAULT_DIR / "Meta"

SCRAPED_LINKS_FILE = META_DIR / "scraped_links.txt"
QUEUE_LINKS_FILE = META_DIR / "queue_links.txt"
FAILED_URLS_FILE = META_DIR / "failed_urls.json"
CRAWL_LOG_FILE = META_DIR / "crawl_log.json"

# In-memory history for 30s rate calculations
# Stores tuples of (timestamp, visited_count, queue_count)
CRAWL_HISTORY = []


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging every static asset request to keep console clean
        pass

    def do_GET(self):
        global CRAWL_HISTORY
        if self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            # Read counts
            visited_count = 0
            if SCRAPED_LINKS_FILE.exists():
                try:
                    with open(SCRAPED_LINKS_FILE, "r", encoding="utf-8") as f:
                        visited_count = sum(1 for line in f if line.strip())
                except Exception:
                    pass

            queue_count = 0
            if QUEUE_LINKS_FILE.exists():
                try:
                    with open(QUEUE_LINKS_FILE, "r", encoding="utf-8") as f:
                        queue_count = sum(1 for line in f if line.strip())
                except Exception:
                    pass

            failed_count = 0
            if FAILED_URLS_FILE.exists():
                try:
                    with open(FAILED_URLS_FILE, "r", encoding="utf-8") as f:
                        failed_count = len(json.load(f))
                except Exception:
                    pass

            # Record history
            current_time = time.time()
            CRAWL_HISTORY.append((current_time, visited_count, queue_count))

            # Clean up history older than 10 minutes (600 seconds)
            cutoff = current_time - 600
            while CRAWL_HISTORY and CRAWL_HISTORY[0][0] < cutoff:
                CRAWL_HISTORY.pop(0)

            # Find closest historical entry to 30 seconds ago
            target_time = current_time - 30
            past_entry = CRAWL_HISTORY[0]
            for entry in reversed(CRAWL_HISTORY):
                if entry[0] <= target_time:
                    past_entry = entry
                    break

            # Calculate deltas
            scraped_30s = visited_count - past_entry[1]
            net_queue_change = queue_count - past_entry[2]
            # Since queue is decreased by visits, actual enqueued = net_change + processed
            added_30s = net_queue_change + scraped_30s

            # Calculate rate and ETC based on session history
            etc_str = "Calculating..."
            rate_per_min = 0.0
            if len(CRAWL_HISTORY) > 1:
                oldest_entry = CRAWL_HISTORY[0]
                time_diff = current_time - oldest_entry[0]
                scraped_diff = visited_count - oldest_entry[1]
                if time_diff > 5 and scraped_diff > 0:
                    rate_per_sec = scraped_diff / time_diff
                    rate_per_min = round(rate_per_sec * 60, 1)
                    if queue_count == 0:
                        etc_str = "Completed"
                    else:
                        seconds_left = queue_count / rate_per_sec
                        if seconds_left < 60:
                            etc_str = f"{int(seconds_left)}s"
                        elif seconds_left < 3600:
                            minutes = int(seconds_left // 60)
                            seconds = int(seconds_left % 60)
                            etc_str = f"{minutes}m {seconds}s"
                        else:
                            hours = int(seconds_left // 3600)
                            minutes = int((seconds_left % 3600) // 60)
                            etc_str = f"{hours}h {minutes}m"
                elif queue_count == 0:
                    etc_str = "Completed"

            # Read latest events
            logs = []
            if CRAWL_LOG_FILE.exists():
                try:
                    with open(CRAWL_LOG_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            logs = data[-15:]
                            logs.reverse()
                except Exception:
                    pass

            stats = {
                "domain": "dev.epicgames.com",
                "visited": visited_count,
                "queued": queue_count,
                "failed": failed_count,
                "scraped_30s": max(0, scraped_30s),
                "added_30s": max(0, added_30s),
                "etc": etc_str,
                "rate_per_min": rate_per_min,
                "logs": logs,
            }
            self.wfile.write(json.dumps(stats).encode("utf-8"))

        elif self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unreal Engine Crawler Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0d0e12;
            --card-bg: rgba(22, 24, 33, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-cyan: #06b6d4;
            --accent-purple: #a855f7;
            --accent-pink: #ec4899;
            --accent-green: #10b981;
            --accent-red: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image:
                radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
        }

        header {
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            padding: 2.5rem 2rem 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-section h1 {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .logo-section p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }

        .domain-tag {
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.25);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.9rem;
            color: var(--accent-cyan);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .domain-tag::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background: var(--accent-cyan);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-cyan);
        }

        main {
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            padding: 0 2rem 3rem 2rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 2rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
        }

        .card-visited::before { background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)); }
        .card-queued::before { background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink)); }
        .card-failed::before { background: linear-gradient(90deg, var(--accent-pink), var(--accent-red)); }
        .card-etc::before { background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green)); }

        .card-title {
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 0.75rem;
        }

        .card-value {
            font-size: 3rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.5rem;
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(180deg, #ffffff 0%, #a3a3a3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .card-desc {
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .rate-badge {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .log-section {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            flex-grow: 1;
            min-height: 400px;
        }

        .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .log-header h2 {
            font-size: 1.4rem;
            font-weight: 700;
        }

        .refresh-indicator {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .progress-circle {
            width: 18px;
            height: 18px;
            transform: rotate(-90deg);
        }

        .progress-circle circle {
            fill: none;
            stroke-width: 3;
        }

        .progress-circle .bg {
            stroke: rgba(255, 255, 255, 0.1);
        }

        .progress-circle .progress {
            stroke: var(--accent-cyan);
            stroke-dasharray: 47;
            stroke-dashoffset: 47;
            transition: stroke-dashoffset 1s linear;
        }

        .log-console {
            background: rgba(10, 11, 14, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            overflow-y: auto;
            flex-grow: 1;
            max-height: 450px;
        }

        .log-row {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.02);
            display: flex;
            gap: 1rem;
        }

        .log-row:last-child {
            border-bottom: none;
        }

        .log-time {
            color: #5b6270;
            flex-shrink: 0;
        }

        .log-badge {
            font-size: 0.75rem;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
            flex-shrink: 0;
            height: fit-content;
        }

        .badge-success {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-error {
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-red);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .log-message {
            word-break: break-all;
        }

        /* Animations */
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.5; }
            50% { transform: scale(1.05); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.5; }
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-green);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-section">
            <h1>Unreal Engine Documentation Crawler</h1>
            <p>Vault Scraper Progress Dashboard</p>
        </div>
        <div class="domain-tag" id="domain-label">dev.epicgames.com</div>
    </header>

    <main>
        <section class="metrics-grid">
            <div class="card card-visited">
                <div class="card-title">Searched / Visited</div>
                <div class="card-value" id="val-visited">-</div>
                <div class="card-desc">
                    <span>Total saved pages</span>
                    <span class="rate-badge" id="rate-scraped" style="color: var(--accent-green);">+0 / 30s</span>
                </div>
            </div>
            <div class="card card-queued">
                <div class="card-title">Remaining In Queue</div>
                <div class="card-value" id="val-queued">-</div>
                <div class="card-desc">
                    <span>Discovered URLs pending</span>
                    <span class="rate-badge" id="rate-added" style="color: var(--accent-cyan);">+0 / 30s</span>
                </div>
            </div>
            <div class="card card-failed">
                <div class="card-title">Failed Requests</div>
                <div class="card-value" id="val-failed">-</div>
                <div class="card-desc">
                    <span>Max retries exhausted</span>
                    <span style="color: var(--accent-red); font-weight: 600;">Errors</span>
                </div>
            </div>
            <div class="card card-etc">
                <div class="card-title">Estimated Completion</div>
                <div class="card-value" id="val-etc">-</div>
                <div class="card-desc">
                    <span>Average crawl rate</span>
                    <span class="rate-badge" id="rate-etc" style="color: var(--accent-purple);">0 pages/min</span>
                </div>
            </div>
        </section>

        <section class="log-section">
            <div class="log-header">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div class="live-dot"></div>
                    <h2>Live Activity Log</h2>
                </div>
                <div class="refresh-indicator">
                    <span>Next update in <strong id="refresh-timer">30</strong>s</span>
                    <svg class="progress-circle">
                        <circle class="bg" cx="9" cy="9" r="7.5"></circle>
                        <circle class="progress" id="progress-bar" cx="9" cy="9" r="7.5"></circle>
                    </svg>
                </div>
            </div>
            <div class="log-console" id="log-console">
                <div style="color: var(--text-secondary); text-align: center; padding: 2rem;">Connecting to scraper data...</div>
            </div>
        </section>
    </main>

    <script>
        let countdown = 30;
        const totalDuration = 30;

        async function updateStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();

                // Update text elements
                document.getElementById('domain-label').innerText = data.domain;

                // Animate numbers
                animateValue('val-visited', data.visited);
                animateValue('val-queued', data.queued);
                animateValue('val-failed', data.failed);

                // Update rates
                document.getElementById('rate-scraped').innerText = `+${data.scraped_30s} / 30s`;
                document.getElementById('rate-added').innerText = `+${data.added_30s} / 30s`;
                document.getElementById('val-etc').innerText = data.etc;
                document.getElementById('rate-etc').innerText = `${data.rate_per_min} pages/min`;

                // Update Logs console
                const consoleDiv = document.getElementById('log-console');
                if (data.logs.length === 0) {
                    consoleDiv.innerHTML = '<div style="color: var(--text-secondary); text-align: center; padding: 2rem;">No logs recorded yet. Waiting for scraper events...</div>';
                } else {
                    consoleDiv.innerHTML = data.logs.map(log => {
                        const isError = log.event.includes('ERROR') || log.event.includes('FAILED');
                        const timeStr = log.timestamp.split('T')[1].split('.')[0];
                        return `
                            <div class="log-row">
                                <span class="log-time">[${timeStr}]</span>
                                <span class="log-badge ${isError ? 'badge-error' : 'badge-success'}">${log.event}</span>
                                <span class="log-message"><strong>${log.message}</strong> - <span style="color: var(--text-secondary)">${log.url}</span></span>
                            </div>
                        `;
                    }).join('');
                }
            } catch (err) {
                console.error("Failed to fetch statistics:", err);
            }
        }

        function animateValue(id, endVal) {
            const el = document.getElementById(id);
            const startVal = parseInt(el.innerText.replace(/,/g, '')) || 0;
            if (startVal === endVal) {
                el.innerText = endVal.toLocaleString();
                return;
            }

            let current = startVal;
            const duration = 500; // ms
            const stepTime = 30;
            const steps = duration / stepTime;
            const increment = (endVal - startVal) / steps;

            let timer = setInterval(() => {
                current += increment;
                if ((increment > 0 && current >= endVal) || (increment < 0 && current <= endVal)) {
                    clearInterval(timer);
                    el.innerText = endVal.toLocaleString();
                } else {
                    el.innerText = Math.round(current).toLocaleString();
                }
            }, stepTime);
        }

        function tick() {
            countdown--;
            document.getElementById('refresh-timer').innerText = countdown;

            // Update circular progress bar
            const circle = document.getElementById('progress-bar');
            const circumference = 2 * Math.PI * 7.5; // ~47.12
            const offset = circumference - (countdown / totalDuration) * circumference;
            circle.style.strokeDashoffset = offset;

            if (countdown <= 0) {
                countdown = 30;
                updateStats();
            }
        }

        // Initial fetch and start ticking
        updateStats();
        setInterval(tick, 1000);
    </script>
</body>
</html>
"""


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Dashboard web app available at: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down dashboard server.")


if __name__ == "__main__":
    run_server()
