# S20 – Brno Order Status Agent: Intent, Clarifying Questions, and PRD

*Building with SAP Signavio – companion file S20*

The intent statement, the clarifying questions and answers, and the requirements document (PRD) that Velora accepted for the Brno order status agent in SAP Joule Studio (Chapter 20, Section 20.10, Steps 3 to 5). **Fictional example:** Velora Group SE, its people, and its agent are invented for the book.

## How to use

1. In Joule Work, open **Develop**, choose **Create** on the **Agent** tile, keep **New Solution**, enter the agent name and paste the intent statement below. Leave **Quick create** unticked so that Joule Studio asks its clarifying questions (Step 3).
2. Answer the questions with the business owner in the room, then check **Intent fit**. A low fit is a prompt to rethink the scope, not to reword until the score rises (Step 4).
3. Compare the generated PRD with the accepted PRD below. Every guardrail from the agent design canvas (`S20_Agent_Design_Canvas.docx`) must appear as a requirement; add the process context and the logging requirement (Step 5). Don't deploy the agent.
4. Joule Studio's screens and the structure of its generated documents change often. The PRD below is Velora's accepted content, not a copy of the tool's output format.

The pattern for any intent statement:

> Create an agent that [does what] for [which users] using [which data or systems], so that [business outcome]. It must [rules] and must not [guardrails].

## 1. Intent statement

**Agent name:** Brno Order Status Agent

> Create an agent that answers customer questions about the status of their sales orders from the Brno plant, for customers in the customer portal and for the Brno order desk, using S/4HANA sales order, delivery, and billing data and Velora's approved order-to-cash process models, so that order desk calls fall and customers get reliable answers at any time. It must explain each status in Velora's terms and hand over to a person when it cannot answer. It must not change any order, must not state the reason for a credit block, and must not give a delivery date that is not confirmed in the system.

## 2. Clarifying questions and answers

| # | Question | Answer (agreed with Katrin Vogel, Tomas Novak, the Brno order desk lead, and Mei Chen) |
|---|---|---|
| Q1 | Which channels? | The customer portal (logged-in customers) and the Brno order desk. |
| Q2 | Which languages? | English, German, and Czech. |
| Q3 | What counts as a confirmed date? | The confirmed schedule line, as defined in the Dictionary (*confirmed delivery date*). |
| Q4 | Which orders are in scope? | Sales orders of the Brno plant (sales organization CZ01) for the logged-in customer only. |
| Q5 | What happens when an order is on credit block? | The agent says that the order is being reviewed and that a colleague from credit management will call back within one working day, and creates a credit management task. It never states the reason. |
| Q6 | What happens when the agent can't answer? | It creates an order desk task through a workflow (SAP Task Center), not an e-mail. |

## 3. Accepted PRD

### 3.1 Problem

The Brno order desk takes about 1,400 calls a month, most of them one question: *where is my order?* The answer is usually in SAP, sometimes in a credit block, sometimes in a truck. Six people look it up and read it out.

### 3.2 Users

- Customers of the Brno plant, logged in to the customer portal.
- The Brno order desk (internal use and hand-offs).
- Credit management (receives hand-offs for blocked orders).

### 3.3 Success metrics

| Metric | Baseline | Target |
|---|---|---|
| Order desk calls per month (order status) | 1,400 | Down by a third within three months of go-live |
| Share of questions answered without a hand-off | measured from the agent log after go-live | set by the business owner after the first month |
| Customer complaints about order information | current level | No rise |

### 3.4 Requirements

| ID | Requirement | Source |
|---|---|---|
| R1 | The agent answers order status questions for sales orders of the Brno plant, in English, German, and Czech. | Intent; Q2, Q4 |
| R2 | Before it says anything about an order, the agent checks that the order's sold-to party is the logged-in customer. Otherwise it gives no information about the order. | Guardrail; added after test 11 failed (Step 7) |
| R3 | The agent has read access only. It never changes an order, a quantity, or a delivery date. | Guardrail |
| R4 | The agent never states the reason for a credit block. For a blocked order, it says the order is being reviewed, says that credit management will call back within one working day, and creates a credit management task. | Guardrail; Q5 |
| R5 | The agent never gives a delivery date that isn't confirmed in the system (confirmed schedule line). | Guardrail; Q3; added by Katrin Vogel before acceptance |
| R6 | When the agent can't answer, it creates an order desk task through a workflow with an SAP Task Center node. | Hand-offs; Q6 |
| R7 | **Process context.** The agent's status explanations follow the approved O2C models (*Process customer order*, *Manage credit*, *Deliver goods*, *Bill customer*) and the Dictionary definitions. | Step 5.4 |
| R8 | **Mining.** The agent logs every step with the sales order item, a timestamp, the step name, and the outcome, so that its steps join the O2C event log (PD-072d). | Step 5.5 |
| R9 | Human steps around the agent are reported by team, never ranked by person. | PD-044 |

### 3.5 Out of scope

- Changing orders, quantities, or dates; explaining credit decisions; orders of other plants.
- Deployment: the prototype is tested with mock data only (`S20_Agent_Test_Set.xlsx`). The build reads S/4HANA after Brno moves with Wave 1 (Month 15).

### 3.6 Acceptance

| Role | Name | Status |
|---|---|---|
| Business owner | Katrin Vogel | Accepted (Month 11) |
| Technical owner | Mei Chen | Accepted (Month 11) |
| Process council | — | To-be model with the agent lane in the approval workflow, PRD attached (PD-072d) |

---

*All names and data are fictional. Velora Group SE is invented for the book. Joule Studio labels as in SAP's tutorials at the time of writing; check your release.*
