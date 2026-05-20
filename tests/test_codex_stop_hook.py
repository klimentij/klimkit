import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "packs" / "codex" / "hooks" / "stop-notify.sh"


def write_executable(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(0o755)


class CodexStopHookTests(unittest.TestCase):
    def run_hook(self, *, tailscale_script: str) -> tuple[str, list[str]]:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            home.mkdir()
            bin_dir = root / "bin"
            bin_dir.mkdir()
            curl_args = root / "curl-args.json"
            config_path = root / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[notifications.telegram]",
                        "enabled = true",
                        'bot_token = "bot-token"',
                        'chat_id = "chat-id"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            write_executable(
                bin_dir / "curl",
                """
                #!/bin/sh
                python3 - "$@" <<'PY'
                import json
                import os
                import sys

                with open(os.environ["CURL_ARGS_FILE"], "w", encoding="utf-8") as fh:
                    json.dump(sys.argv[1:], fh)
                PY
                """,
            )
            write_executable(bin_dir / "tailscale", tailscale_script)
            payload = {
                "session_id": "thread-1",
                "turn_id": "turn-1",
                "last_assistant_message": "Implemented and verified the notification change.",
                "cwd": "/home/ubuntu/klimkit",
            }
            env = {
                **os.environ,
                "HOME": str(home),
                "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
                "KLIMKIT_CONFIG": str(config_path),
                "CURL_ARGS_FILE": str(curl_args),
            }
            result = subprocess.run(
                [str(HOOK)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

            args = json.loads(curl_args.read_text(encoding="utf-8")) if curl_args.exists() else []
            return result.stdout, args

    def telegram_text(self, args: list[str]) -> str:
        for arg in args:
            if arg.startswith("text="):
                return arg.removeprefix("text=")
        self.fail("curl arguments did not include Telegram text payload")

    def test_notification_includes_switchboard_then_direct_code_server_url(self) -> None:
        stdout, args = self.run_hook(
            tailscale_script="""
            #!/bin/sh
            if [ "$1" = "status" ] && [ "$2" = "--json" ]; then
              printf '%s\n' '{"Self":{"HostName":"odev","DNSName":"odev.tail11c448.ts.net."}}'
              exit 0
            fi
            exit 1
            """,
        )

        self.assertEqual(json.loads(stdout), {"continue": True})
        text = self.telegram_text(args)
        self.assertIn("Open in Klimkit Switchboard", text)
        self.assertIn("Open code-server directly", text)
        self.assertLess(text.index("Open in Klimkit Switchboard"), text.index("Open code-server directly"))
        self.assertIn(
            "https://odev.tail11c448.ts.net/proxy/4721/#session=thread-1&machine=odev&folder=%2Fhome%2Fubuntu%2Fklimkit",
            text,
        )
        self.assertIn("https://odev.tail11c448.ts.net/?folder=/home/ubuntu/klimkit", text)
        self.assertIn("parse_mode=HTML", args)

    def test_notification_omits_direct_code_server_url_without_tailscale_dns(self) -> None:
        stdout, args = self.run_hook(
            tailscale_script="""
            #!/bin/sh
            exit 1
            """,
        )

        self.assertEqual(json.loads(stdout), {"continue": True})
        text = self.telegram_text(args)
        self.assertNotIn("Open in Klimkit Switchboard", text)
        self.assertNotIn("Open code-server directly", text)
        self.assertNotIn("https:///?folder=", text)


if __name__ == "__main__":
    unittest.main()
