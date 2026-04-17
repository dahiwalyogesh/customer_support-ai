## Live Demo
[Open the app](https://customersupport-ai.streamlit.app)
# Customer Support AI Assistant Prototype

## Overview
This project is a customer support AI assistant prototype for an e-commerce business.

The assistant handles low-risk customer queries such as return policy, shipping, cancellations, damaged items, and order tracking. It uses a small structured knowledge base and rule-based retrieval to return grounded answers. High-risk requests such as refunds, compensation, payment disputes, legal issues, fraud concerns, and policy exceptions are escalated to a human agent.

## Business problem
Customer support teams spend significant time answering repetitive low-risk questions. Automating these queries can improve response speed and reduce workload. However, not all support cases are safe to automate. Requests involving refunds, complaints, disputes, or exceptions require human review.

This project demonstrates a simple AI support workflow that automates low-risk queries while adding guardrails for high-risk cases.

## Solution
The prototype uses:
- a structured FAQ and policy knowledge base in JSON
- sample order data in CSV
- rule-based guardrails for risky topics
- simple retrieval based on token overlap
- confidence thresholding to avoid weak matches
- fallback to human escalation when no reliable answer is found
- logging of interactions and escalations

## Key features
- Answers FAQ and policy questions
- Handles order tracking with order ID lookup
- Escalates high-risk requests to human support
- Shows answer source and confidence score
- Logs interactions in `chat_history.csv`
- Logs risky cases in `escalations.csv`
- Includes evaluation script for testing answer, escalation, and fallback behavior

## Example supported questions
- What is your return policy?
- How long does shipping take?
- Do you ship internationally?
- Can I cancel my order?
- What if my item arrives damaged?
- Where is my order?

## Example escalated questions
- Give me a refund now
- Change my address
- I want compensation
- Cancel payment now
- Make an exception to your policy
- I want to sue the company

## Example fallback questions
- Do you offer gift wrapping?
- Tell me about warranty extensions
- Can I subscribe for monthly deliveries?

## Evaluation result
The prototype was tested on 19 sample queries covering:
- FAQ answering
- high-risk escalation
- fallback handling

After tuning the retrieval confidence threshold, the system achieved:

- **Overall accuracy: 100.00% on the current test set**
- **FAQ answer accuracy: 10/10**
- **Guardrail accuracy: 6/6**
- **Fallback accuracy: 3/3**

This is an early prototype result on a small evaluation set, not a production benchmark.

## Project structure
```text
customer-support-ai/
├── app.py
├── config.py
├── utils.py
├── retrieval.py
├── guardrails.py
├── logger.py
├── evaluate.py
├── kb.json
├── orders.csv
├── chat_history.csv
├── escalations.csv
├── sample_questions.txt
├── requirements.txt
└── README.md
