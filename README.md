# alessandra-ai-portfolio

Practical AI & data projects — from automation to dashboards and analytics.

## About me

With a background in the utilities and energy sector, I now lead planning, monitoring, and operational management of maintenance and fault-handling
activities on public lighting infrastructure. I oversee contracts, SLAs, and resource allocation, ensuring efficiency, service continuity, and
compliance with company standards.

Through Business Intelligence tools (Snowflake, Qlik Sense, Power BI), I provide structured reporting and clear visibility into operational
performance to support decision-making.

I already use AI tools to automate parts of my daily workflow, and I'm building on this by developing broader AI and data automation skills —
this repository collects that hands-on work.

## Hands-on AI/automation projects (code in this repo)

| Project | Description | Tech |
|---|---|---|
| [Project 01 — Automated Operations Performance Reporting](./project-01-facility-management) | End-to-end pipeline (synthetic data): data quality, fault-recidivism KPI engine, live-formula Excel reporting, AI executive summary, management slides, monthly automated orchestration | Python, pandas, Excel (live formulas), Canva, Claude |
| [Project 02 — Operations Performance Chatbot MVP](./project-02-chatbot-mvp) | Claude Project configured as a Q&A assistant over Project 01's KPI report, with custom instructions that ground every answer in the underlying figures and decline out-of-scope questions rather than guessing | Claude Projects, prompt engineering |
| [Project 03 — AI + Project Management (Product Launch Planning)](./project-03-lancio-prodotto) | WBS breakdown, three-point (PERT) duration estimates, Critical Path Method and float analysis for a generic product-launch scenario, translated into a live-formula Excel Gantt chart with the critical path highlighted | Excel (live formulas, CPM/PERT), openpyxl, Claude |

**Key result (2025, synthetic dataset)**: 28.7% of assets with a fault had repeated interventions, generating 52% of all work orders for the year — concentrated, not diffuse, problem pattern.

**Key result**: every answer stays grounded in Project 01's actual KPI figures, with the assistant explicitly declining questions outside that data rather than inventing numbers.

**Key result (generic scenario, 15-task WBS)**: the critical path runs through product development and certification — not marketing or sales — with certification alone accounting for ~21 of the 64 working days to launch.

## Professional context (proprietary, not published here)

These dashboards were built with company tools and data at my current role — described here for context; source and data are not publishable.

| Project | Description | Tech |
|---|---|---|
| Infrastructure Maintenance Dashboard | Operational dashboard tracking maintenance work orders, with breakdowns by time, location, and status to support planning decisions | Qlik Sense, SQL |
| Contract & Order Tracking Dashboard | Dashboard for monitoring contract capacity, upcoming deadlines, and orders in progress, supporting resource planning and timely follow-up | Qlik Sense, SQL |
| Fault Monitoring & Root Cause Dashboard | Dashboard tracking recurring faults, root causes, and intervention response times, supporting reliability analysis and process improvement | Qlik Sense, SQL |
