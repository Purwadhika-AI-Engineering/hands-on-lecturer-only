# JC AI Engineer — Hands-on Materials

This repository contains the hands-on learning materials for the **JC AI Engineer program at Purwadhika**, intended specifically for **lecturers/instructors**.

> [!IMPORTANT]
> **This repository is for lecturer use only.**
>
> Do **not** share or distribute this repository directly to students.
>
> When conducting hands-on sessions, lecturers should copy the relevant materials into the **class repository** and share the class repository with students instead.

---

## About This Repository

This repository serves as the central source for hands-on materials used in the **JC AI Engineer learning program**.

The materials are designed to support lecturers during hands-on sessions, including:

- Notebook-based exercises
- Coding examples
- Step-by-step implementations
- Supporting materials for each learning module
- Exercises and activities that can be used during class

The repository is maintained for **lecturer preparation and teaching purposes**.

---

## Course Modules

The JC AI Engineer program consists of six main modules:

| Module | Topic | Status |
| --- | --- | --- |
| **Module 1** | Programming Fundamentals and Statistics | Coming Soon |
| **Module 2** | ML and AI Fundamental | Coming Soon |
| **Module 3** | LLM and Agentic AI | ✅ Available |
| **Module 4** | Computer Vision | Coming Soon |
| **Module 5** | AI/ML Deployment | Coming Soon |
| **Module 6** | Automation with n8n | Coming Soon |

### Currently Available

At the moment, **Module 3 — LLM and Agentic AI** is available in this repository.

Materials for the other modules will be added progressively.

---

## How to Use This Repository

The recommended workflow is:

```text
Lecturer
   │
   ├── Clone lecturer-only repository
   │
   ├── Prepare / review hands-on materials
   │
   ├── Create class repository
   │
   ├── Copy relevant hands-on materials
   │
   └── Commit & push materials
           │
           ▼
      Class Repository
           │
           ▼
         Students
```

### 1. Clone This Repository

Each lecturer should clone this repository to their local machine.

```bash
git clone <repository-url>
cd hands-on-lecturer-only
```

### 2. Create a Repository for Your Class

Before conducting a hands-on session, create a **separate repository for the class**.

For example:

```text
hands-on-jc-ai-engineer-class-a
```

The class repository is the repository that will eventually be accessed by students.

### 3. Prepare the Hands-on Materials

Select the relevant materials from this repository based on the session or chapter being taught.

For example:

```text
hands-on-lecturer-only/
└── modul-3/
    └── ...
```

Review and prepare the materials before the class as necessary.

### 4. Copy the Materials to the Class Repository

Copy the relevant materials into the class repository.

You may then commit and push the materials:

```bash
git add .
git commit -m "Add Module 3 hands-on materials"
git push
```

### 5. Install the Required Dependencies

Some hands-on sessions may require additional software, libraries, packages, API keys, or other configuration.

Please install and configure the required dependencies according to the relevant chapter or hands-on material.

For example:

```bash
pip install <required-package>
```

> [!NOTE]
> Always check the instructions inside the relevant hands-on material for the required environment and dependencies.

---

## ⚠️ Lecturer Repository vs Class Repository

There are **two different types of repositories** involved in the teaching workflow.

### Lecturer-only Repository

This repository:

- Contains the official lecturer hands-on materials
- Is used as the source/reference material
- Is intended for lecturers
- **Must not be directly shared with students**

### Class Repository

This repository:

- Is created specifically for a particular class
- Contains the hands-on materials used by that class
- Can be shared with students
- May contain additional materials, modifications, or exercises prepared by the lecturer

### The Rule

> **Never directly share this lecturer-only repository with students.**

Instead:

```text
Lecturer-only Repository
        │
        │ copy relevant materials
        ▼
   Class Repository
        │
        │ share
        ▼
     Students
```

---

## Repository and Access Guidelines

Please keep the following guidelines in mind:

1. **Do not share this repository directly with students.**
2. Do not give students access to the lecturer-only repository unless explicitly authorized.
3. Use a separate repository for each class when appropriate.
4. Only copy the materials that are relevant to the class/session.
5. Avoid committing sensitive information such as:
   - API keys
   - Passwords
   - Access tokens
   - Credentials
   - Private configuration
6. If a hands-on requires an API key or other secret, use an appropriate `.env` file or secret-management mechanism and **never commit the actual secret**.
7. If you modify hands-on material for teaching purposes, make sure the changes do not unintentionally expose lecturer-only materials or answers to students.

---

## 🧑‍🏫 Lecturer Workflow

### Before Class

- Pull the latest changes from this repository.
- Review the relevant hands-on material.
- Check required dependencies and environment configuration.
- Test the notebook/code locally.
- Prepare the class repository.
- Copy the required materials into the class repository.

### During Class

- Use the class repository as the source for student materials.
- Guide students through the hands-on activities.
- Modify or extend the exercises when appropriate.

### After Class

- Commit any materials that should remain available in the class repository.
- Keep lecturer-only materials and internal notes in the lecturer repository when they should not be exposed to students.

---

## 📁 Repository Structure

The repository is organized by learning module.

The structure may evolve as additional modules are added.

```text
hands-on-lecturer-only/
│
├── modul-1/
│   └── ...
│
├── modul-2/
│   └── ...
│
├── modul-3/
│   └── ...
│
├── modul-4/
│   └── ...
│
├── modul-5/
│   └── ...
│
└── modul-6/
    └── ...
```

Currently, **Module 3** is available. Other modules will be added progressively.

---

## Keeping Materials Up to Date

This repository is the source of truth for the lecturer hands-on materials.

Before preparing a new class, lecturers are encouraged to make sure they have the latest version:

```bash
git pull origin main
```

If new materials or updates are available, use the latest version when preparing the class repository.

---

## 📝 Improving the Materials

If you identify:

- Incorrect instructions
- Broken code
- Outdated dependencies
- Typographical errors
- Unclear explanations
- Improvements for hands-on activities

please update the material through the appropriate Git workflow or communicate the issue to the person responsible for maintaining the curriculum.

When making changes, consider whether the change should be:

- applied to the official lecturer material, or
- kept only in a specific class repository.

---

## 📌 Quick Reminder

Before every class:

```text
1. Pull the latest lecturer materials
2. Review the relevant hands-on
3. Prepare the required environment
4. Create / prepare the class repository
5. Copy the required materials
6. Commit & push to the class repository
7. Share the CLASS repository with students
```

> **Lecturer Repository ≠ Student Repository**

The lecturer-only repository is the **source material**.

The class repository is what should be **shared with students**.

---

## 📖 Module Overview

### Module 1 — Programming Fundamentals and Statistics

Fundamental programming concepts and statistics required for AI/ML development.

**Status:** Coming Soon

### Module 2 — ML and AI Fundamental

Fundamental concepts and practical implementation of Machine Learning and Artificial Intelligence.

**Status:** Coming Soon

### Module 3 — LLM and Agentic AI

Hands-on materials covering Large Language Models (LLMs) and Agentic AI.

**Status:** Available

### Module 4 — Computer Vision

Hands-on materials covering Computer Vision concepts and applications.

**Status:** Coming Soon

### Module 5 — AI/ML Deployment

Hands-on materials covering deployment of AI/ML applications and services.

**Status:** Coming Soon

### Module 6 — Automation with n8n

Hands-on materials covering workflow automation using n8n.

**Status:** Coming Soon

---

## 👨‍🏫 Intended Audience

This repository is intended for:

- JC AI Engineer lecturers
- Authorized curriculum / teaching staff

It is **not intended to be used as a direct student repository**.

---

## Usage

The materials in this repository are intended for use within the Purwadhika JC AI Engineer teaching environment.

Please follow the applicable Purwadhika policies regarding the use, modification, and distribution of these materials.
