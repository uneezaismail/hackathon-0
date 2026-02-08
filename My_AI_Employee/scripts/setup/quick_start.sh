#!/bin/bash
# Quick Start - Process Pending Items with Ralph Loop

cd /mnt/d/hackathon-0/My_AI_Employee

echo "=========================================="
echo "Gold Tier - Process Pending Items"
echo "=========================================="
echo ""
echo "Pending items:"
ls -1 AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | nl
echo ""
echo "Starting Claude Code..."
echo ""
echo "After Claude starts, type:"
echo "  /ralph-wiggum-runner"
echo ""
echo "Or say:"
echo "  Start Ralph Wiggum Loop to process all tasks"
echo ""
echo "=========================================="
echo ""

# Start Claude
claude
