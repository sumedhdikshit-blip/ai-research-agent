"""
Leave Management MCP Server using FastMCP.

Features:
  - Apply for leave
  - Approve / Reject leave
  - Cancel leave
  - Check leave balance
  - List leaves (by employee, status, date range)
  - Admin: add leave balance

Run:
    pip install fastmcp
    python leave_management_mcp.py
"""

from datetime import date, datetime, timedelta
from typing import Literal
from mcp.server.fastmcp import FastMCP

# ── In-memory store (replace with DB in production) ────────────────────────────
# Structure: { emp_id: { "name": str, "balance": {type: days}, "leaves": [...] } }

EMPLOYEES: dict[str, dict] = {
    "E001": {
        "name": "Alice Sharma",
        "balance": {"casual": 12, "sick": 10, "earned": 15},
        "leaves": [],
    },
    "E002": {
        "name": "Bob Mehta",
        "balance": {"casual": 12, "sick": 10, "earned": 15},
        "leaves": [],
    },
    "E003": {
        "name": "Carol Nair",
        "balance": {"casual": 12, "sick": 10, "earned": 15},
        "leaves": [],
    },
}

LeaveType   = Literal["casual", "sick", "earned"]
LeaveStatus = Literal["pending", "approved", "rejected", "cancelled"]

_leave_counter = 0

def _new_leave_id() -> str:
    global _leave_counter
    _leave_counter += 1
    return f"LV{_leave_counter:04d}"

def _working_days(start: date, end: date) -> int:
    """Count Mon–Fri days between start and end (inclusive)."""
    days = 0
    current = start
    while current <= end:
        if current.weekday() < 5:   # 0=Mon … 4=Fri
            days += 1
        current += timedelta(days=1)
    return days

def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def _get_emp(emp_id: str) -> dict:
    emp = EMPLOYEES.get(emp_id)
    if not emp:
        raise ValueError(f"Employee '{emp_id}' not found.")
    return emp

# ── MCP Server ──────────────────────────────────────────────────────────────────

mcp = FastMCP("LeaveManagement", json_response=True)


# ──────────────────────────────────────────────────────────────────────────────
# TOOLS
# ──────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def apply_leave(
    emp_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str,
) -> dict:
    """
    Apply for leave.

    Args:
        emp_id:     Employee ID (e.g. E001)
        leave_type: One of 'casual', 'sick', 'earned'
        start_date: Start date in YYYY-MM-DD format
        end_date:   End date in YYYY-MM-DD format
        reason:     Reason for leave

    Returns:
        Leave application details with a generated leave_id.
    """
    emp = _get_emp(emp_id)

    if leave_type not in ("casual", "sick", "earned"):
        raise ValueError("leave_type must be one of: casual, sick, earned")

    start = _parse_date(start_date)
    end   = _parse_date(end_date)

    if start > end:
        raise ValueError("start_date must be before or equal to end_date.")
    if start < date.today():
        raise ValueError("Cannot apply leave for a past date.")

    days_needed = _working_days(start, end)
    balance     = emp["balance"][leave_type]

    if days_needed > balance:
        raise ValueError(
            f"Insufficient {leave_type} leave balance. "
            f"Available: {balance} day(s), Required: {days_needed} day(s)."
        )

    leave_id = _new_leave_id()
    record = {
        "leave_id":   leave_id,
        "emp_id":     emp_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date":   end_date,
        "days":       days_needed,
        "reason":     reason,
        "status":     "pending",
        "applied_on": str(date.today()),
        "remarks":    "",
    }
    emp["leaves"].append(record)

    return {
        "success": True,
        "message": f"Leave applied successfully. ID: {leave_id}",
        "leave":   record,
        "balance_after_approval": balance - days_needed,
    }


@mcp.tool()
def approve_leave(leave_id: str, approver_id: str, remarks: str = "") -> dict:
    """
    Approve a pending leave application.

    Args:
        leave_id:    Leave ID to approve (e.g. LV0001)
        approver_id: Employee ID of the approver / manager
        remarks:     Optional approval remarks

    Returns:
        Updated leave record.
    """
    for emp in EMPLOYEES.values():
        for leave in emp["leaves"]:
            if leave["leave_id"] == leave_id:
                if leave["status"] != "pending":
                    raise ValueError(
                        f"Leave {leave_id} is already '{leave['status']}'. "
                        "Only pending leaves can be approved."
                    )
                leave_type = leave["leave_type"]
                emp["balance"][leave_type] -= leave["days"]
                leave["status"]     = "approved"
                leave["remarks"]    = remarks
                leave["approver"]   = approver_id
                leave["actioned_on"] = str(date.today())
                return {
                    "success": True,
                    "message": f"Leave {leave_id} approved.",
                    "leave":   leave,
                    "remaining_balance": emp["balance"][leave_type],
                }
    raise ValueError(f"Leave ID '{leave_id}' not found.")


@mcp.tool()
def reject_leave(leave_id: str, approver_id: str, remarks: str = "") -> dict:
    """
    Reject a pending leave application.

    Args:
        leave_id:    Leave ID to reject
        approver_id: Employee ID of the approver / manager
        remarks:     Reason for rejection

    Returns:
        Updated leave record.
    """
    for emp in EMPLOYEES.values():
        for leave in emp["leaves"]:
            if leave["leave_id"] == leave_id:
                if leave["status"] != "pending":
                    raise ValueError(
                        f"Leave {leave_id} is already '{leave['status']}'."
                    )
                leave["status"]      = "rejected"
                leave["remarks"]     = remarks
                leave["approver"]    = approver_id
                leave["actioned_on"] = str(date.today())
                return {
                    "success": True,
                    "message": f"Leave {leave_id} rejected.",
                    "leave":   leave,
                }
    raise ValueError(f"Leave ID '{leave_id}' not found.")


@mcp.tool()
def cancel_leave(leave_id: str, emp_id: str) -> dict:
    """
    Cancel a leave (pending or approved).
    Approved leaves refund the balance automatically.

    Args:
        leave_id: Leave ID to cancel
        emp_id:   Employee who owns the leave

    Returns:
        Updated leave record with refund info if applicable.
    """
    emp = _get_emp(emp_id)
    for leave in emp["leaves"]:
        if leave["leave_id"] == leave_id:
            if leave["status"] == "cancelled":
                raise ValueError("Leave is already cancelled.")
            if leave["status"] == "rejected":
                raise ValueError("Rejected leaves cannot be cancelled.")

            refunded = False
            if leave["status"] == "approved":
                emp["balance"][leave["leave_type"]] += leave["days"]
                refunded = True

            leave["status"]      = "cancelled"
            leave["actioned_on"] = str(date.today())
            return {
                "success":  True,
                "message":  f"Leave {leave_id} cancelled."
                            + (" Balance refunded." if refunded else ""),
                "leave":    leave,
                "balance":  emp["balance"],
            }
    raise ValueError(f"Leave ID '{leave_id}' not found for employee '{emp_id}'.")


@mcp.tool()
def get_leave_balance(emp_id: str) -> dict:
    """
    Get current leave balance for an employee.

    Args:
        emp_id: Employee ID

    Returns:
        Leave balance breakdown by type.
    """
    emp = _get_emp(emp_id)
    return {
        "emp_id":  emp_id,
        "name":    emp["name"],
        "balance": emp["balance"],
    }


@mcp.tool()
def list_leaves(
    emp_id: str | None = None,
    status: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    """
    List leave applications with optional filters.

    Args:
        emp_id:    Filter by employee ID (optional)
        status:    Filter by status: pending | approved | rejected | cancelled (optional)
        from_date: Filter leaves starting on or after this date (YYYY-MM-DD, optional)
        to_date:   Filter leaves starting on or before this date (YYYY-MM-DD, optional)

    Returns:
        List of matching leave records.
    """
    results = []
    employees_to_check = (
        {emp_id: EMPLOYEES[emp_id]} if emp_id and emp_id in EMPLOYEES
        else EMPLOYEES
    )

    fd = _parse_date(from_date) if from_date else None
    td = _parse_date(to_date)   if to_date   else None

    for eid, emp in employees_to_check.items():
        for leave in emp["leaves"]:
            if status and leave["status"] != status:
                continue
            ls = _parse_date(leave["start_date"])
            if fd and ls < fd:
                continue
            if td and ls > td:
                continue
            results.append({**leave, "employee_name": emp["name"]})

    return {
        "count":  len(results),
        "leaves": results,
    }


@mcp.tool()
def add_employee(emp_id: str, name: str) -> dict:
    """
    Register a new employee with default leave balances.

    Args:
        emp_id: Unique employee ID (e.g. E004)
        name:   Full name

    Returns:
        New employee record.
    """
    if emp_id in EMPLOYEES:
        raise ValueError(f"Employee '{emp_id}' already exists.")
    EMPLOYEES[emp_id] = {
        "name":    name,
        "balance": {"casual": 12, "sick": 10, "earned": 15},
        "leaves":  [],
    }
    return {
        "success": True,
        "message": f"Employee {emp_id} ({name}) added.",
        "employee": EMPLOYEES[emp_id],
    }


@mcp.tool()
def credit_leave_balance(
    emp_id: str,
    leave_type: str,
    days: int,
) -> dict:
    """
    Credit additional leave days to an employee's balance (admin use).

    Args:
        emp_id:     Employee ID
        leave_type: One of 'casual', 'sick', 'earned'
        days:       Number of days to credit (positive integer)

    Returns:
        Updated balance.
    """
    if leave_type not in ("casual", "sick", "earned"):
        raise ValueError("leave_type must be one of: casual, sick, earned")
    if days <= 0:
        raise ValueError("days must be a positive integer.")
    emp = _get_emp(emp_id)
    emp["balance"][leave_type] += days
    return {
        "success":         True,
        "message":         f"Credited {days} {leave_type} day(s) to {emp_id}.",
        "updated_balance": emp["balance"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# RESOURCES
# ──────────────────────────────────────────────────────────────────────────────

@mcp.resource("employee://{emp_id}/profile")
def employee_profile(emp_id: str) -> dict:
    """Get full employee profile including balance and leave history."""
    emp = _get_emp(emp_id)
    return {
        "emp_id":  emp_id,
        "name":    emp["name"],
        "balance": emp["balance"],
        "leaves":  emp["leaves"],
    }


@mcp.resource("leave://{leave_id}")
def leave_detail(leave_id: str) -> dict:
    """Get details of a specific leave by ID."""
    for emp in EMPLOYEES.values():
        for leave in emp["leaves"]:
            if leave["leave_id"] == leave_id:
                return {**leave, "employee_name": emp["name"]}
    raise ValueError(f"Leave ID '{leave_id}' not found.")


@mcp.resource("policy://leave-types")
def leave_policy() -> dict:
    """Return the company's leave policy."""
    return {
        "leave_types": {
            "casual": {
                "annual_quota": 12,
                "max_consecutive": 3,
                "carry_forward": False,
                "notes": "For personal errands and short breaks.",
            },
            "sick": {
                "annual_quota": 10,
                "max_consecutive": None,
                "carry_forward": False,
                "notes": "Medical leave. Certificate needed for > 3 days.",
            },
            "earned": {
                "annual_quota": 15,
                "max_consecutive": 15,
                "carry_forward": True,
                "notes": "Accrued over service. Plan in advance.",
            },
        },
        "working_days": "Monday to Friday",
        "notice_period": "Casual: 1 day | Earned: 7 days",
    }


# ──────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ──────────────────────────────────────────────────────────────────────────────

@mcp.prompt()
def apply_leave_prompt(emp_id: str, leave_type: str, days: int) -> str:
    """Generate a polite leave application message."""
    return (
        f"Write a brief, professional leave application for employee {emp_id} "
        f"requesting {days} day(s) of {leave_type} leave. "
        "Include a polite opening, reason placeholder [REASON], and a closing."
    )


@mcp.prompt()
def leave_summary_prompt(emp_id: str) -> str:
    """Generate a prompt to summarise an employee's leave status."""
    return (
        f"Summarise the leave history and current balance for employee {emp_id}. "
        "Highlight any pending applications and suggest whether they have enough "
        "balance for a 5-day earned leave."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

mcp.run(transport="streamable-http")