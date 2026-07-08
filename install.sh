#!/data/data/com.termux/files/usr/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pkg update -y
pkg install -y python git curl openssl coreutils
mkdir -p "$HOME/.local/bin" "$HOME/.nexus_ai_protector"

cat > "$HOME/.local/bin/nexus-ai-protector" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
python3 "$SCRIPT_DIR/nexus_ai_protector.py" "$@"
EOF

chmod +x "$HOME/.local/bin/nexus-ai-protector"

echo "Advanced NexusAIProtector installation completed."
echo "Run: nexus-ai-protector scan"
echo "Run: nexus-ai-protector install"
