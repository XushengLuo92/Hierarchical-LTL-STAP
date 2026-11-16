window.DEMOS = [
  {
    "id": 1,
    "title": "Bin service",
    "description": "Two subtasks coordinate collection, disposal, emptying, and return at desk D5.",
    "note": "R5 completes p200 at step 23; R1 completes p100 at step 35. The specification does not impose a pickup-before-empty order between these children.",
    "obligations": [
      "p100: collect the bin, carry it, dispose of it, and reset.",
      "p200: empty at G, then return and reset at D5.",
      "A robot carrying the bin must avoid public cells."
    ],
    "robots": 6,
    "label": "Scenario 1",
    "meta": "Planner case 12 · minmax · seed 42",
    "video": "demo/generated/scenario_01.mp4",
    "replay": "demo/generated/scenario_01.json",
    "validation": "demo/generated/scenario_01.validation.json",
    "poster": "demo/generated/scenario_01.png"
  },
  {
    "id": 2,
    "title": "Printed-document distribution",
    "description": "Deliver printed copies from P to three desks, preserving the carrying and delivery requirements.",
    "note": "R6 serves D10 and D7; R4 serves D5. The root completes at step 32.",
    "obligations": [
      "Deliver to D10, D7, and D5.",
      "Each delivery must be followed by a step without carry.",
      "Avoid public cells while carrying a document."
    ],
    "robots": 6,
    "label": "Scenario 2",
    "meta": "Planner case 13 · minmax · seed 42",
    "video": "demo/generated/scenario_02.mp4",
    "replay": "demo/generated/scenario_02.json",
    "validation": "demo/generated/scenario_02.validation.json",
    "poster": "demo/generated/scenario_02.png"
  },
  {
    "id": 3,
    "title": "Photos, delivery, and guidance",
    "description": "Three parent missions combine meeting-room photography, confidential delivery, and visitor guidance.",
    "note": "Individual photo leaves complete their parent, which contributes to the root alongside delivery and guidance. The root completes at step 36.",
    "obligations": [
      "Take photos in M1, M4, and M6; use the camera only in meeting rooms.",
      "Deliver the confidential document from D5 to D3 without carrying through public cells.",
      "Guide the visitor from D11 to M6."
    ],
    "robots": 6,
    "label": "Scenario 3",
    "meta": "Planner case 14 · minmax · seed 42",
    "video": "demo/generated/scenario_03.mp4",
    "replay": "demo/generated/scenario_03.json",
    "validation": "demo/generated/scenario_03.validation.json",
    "poster": "demo/generated/scenario_03.png"
  },
  {
    "id": 4,
    "title": "A combined four-level mission",
    "description": "All three scenario families run together in a hierarchy with ten concrete leaf tasks.",
    "note": "The photo task p301 groups p401, p402, and p403. All ten leaf tasks contribute to root completion at step 64.",
    "obligations": [
      "Complete the bin-service and printed-copy branches.",
      "Complete the office-assistance branch: photos, delivery, and guidance.",
      "Resolve child obligations before their parent completion is shown."
    ],
    "robots": 6,
    "label": "Scenario 4",
    "meta": "Planner case 21 · minmax · seed 42",
    "video": "demo/generated/scenario_04.mp4",
    "replay": "demo/generated/scenario_04.json",
    "validation": "demo/generated/scenario_04.validation.json",
    "poster": "demo/generated/scenario_04.png"
  }
];
