# Hiring Request Workflow Module

## Overview
Custom recruitment hiring request workflow enabling multilevel approval before recruitment starts.

## Features
- Requesters create hiring requests for job positions with number of positions.
- Requests pass through:
  - Recruitment Officer approval,
  - Recruitment Administrator approval,
  - General Manager approval.
- Detailed rejection reasons tracked via wizard.
- Email notifications at each step.
- On final approval, job position updated, recruitment officer notified to start recruitment.
- Access and visibility controlled by user groups.
- Integration with standard Odoo Recruitment module.

## Installation
- Add this module to your Odoo addons.
- Update app list and install 'Hiring Request Workflow'.
- Assign users to appropriate groups:
  - Hiring Request User
  - Recruitment Officer
  - Recruitment Administrator
  - General Manager (existing group: visa_process.group_service_request_general_manager)

## Usage
- Requesters create and submit hiring requests.
- Recruitment officers/admins/GM approve or reject requests with reasons.
- On GM approval, the recruitment officer starts standard recruitment phases.