# HR Employee Change Request Module for Odoo 15

## Overview

This module allows internal employees to request changes to their personal information (marital status, mobile number, email address) which must then be approved or rejected by HR managers.

## Features

- Employees can create requests for updating marital status, mobile number, or email.
- Requests have unique sequence numbers (e.g., ECR0001).
- HR Managers (Odoo's standard HR group) can view and approve/reject all requests.
- Employees can only see their own requests.
- Email notifications and Odoo activity notifications are sent:
  - To HR managers when new requests are submitted.
  - To employees when requests are approved or rejected.
- Smart button on employee form showing count of change requests and listing them.
- Uses standard Odoo groups (`Employee` and `HR Manager`) for access control.
- Supports `custom_employee_type` field to differentiate internal/external employees.
- Uses standard `marital` selection field values for marital status changes.

## Installation

1. Copy this module folder (`hr_employee_change_request/`) into your Odoo addons directory.
2. Update app list and install the module `HR Employee Change Request`.
3. Assign internal employees to Odoo's standard Employee group and HR managers to HR Manager group.
4. Employee users must have linked `hr.employee` records.
5. To configure emails, make sure outgoing mail servers are properly set.

## Usage

- Employees:
  - Go to Employee Change Requests menu.
  - Create new request and select change type and new value.
  - Submit for approval.
- HR Managers:
  - Get notified of new requests.
  - Approve or reject requests.
  - Upon approval, the hr.employee record is updated automatically.
- Employee form shows a smart button indicating number of requests and lets user view them directly.

## Notes

- Employees cannot edit requests once submitted.
- Only HR Managers can approve or reject.
- In future, you can extend or differentiate external employee requests based on the `custom_employee_type` field.

## Support

For support or customization, contact your Odoo partner or developer.