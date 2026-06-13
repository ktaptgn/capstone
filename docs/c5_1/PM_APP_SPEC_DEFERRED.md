# PM_APP_SPEC_DEFERRED.md

## Status

Activated by separate user instruction on 2026-05-25 as an imported mobile web UI draft.

## Planned Role

The PM app will be a field execution interface for PM workers.

Planned screens:

- Today PM List
- Truck Detail
- PM Checklist
- PM History
- PM Request Response
- Limited Chatbot

## C5.1 Boundary

The PM worker app is a file-based work order consumption layer. It reads generated C5.1 work order and log snapshots from `public/c5_1/`.

It must not run the C5.1 simulation, add native Android build files, add RL training, or implement Drop Zone scenarios.
