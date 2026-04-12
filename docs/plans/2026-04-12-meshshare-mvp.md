# MeshShare MVP Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a Linux-hosted web service that shares files, discovers peer instances, and enforces configurable allow/deny rules, with MeshNet as an optional security layer.

**Architecture:** Use a small FastAPI app with three concerns: configuration loading, peer registry/heartbeat state, and HTTP endpoints for the web UI + JSON APIs. Store peer state in memory for the MVP and keep file sharing read-only from a configured directory.

**Tech Stack:** Python 3.11, FastAPI, pytest, httpx, Just

---

### Task 1: Scaffold the repo
**Objective:** Create the base project layout, packaging, docs, and automation commands.

### Task 2: Write peer-registry tests first
**Objective:** Define registration, heartbeat freshness, and allow/deny behavior with failing tests.

### Task 3: Implement peer registry
**Objective:** Add the minimum registry/config code to satisfy the tests.

### Task 4: Write API tests first
**Objective:** Define the expected file list, download, and peer API behavior.

### Task 5: Implement FastAPI endpoints
**Objective:** Add the web app, JSON APIs, and static HTML response needed for the MVP.

### Task 6: Verify and publish
**Objective:** Run tests, create the GitHub repo, push the initial version, and open a review thread tagging Nick.
