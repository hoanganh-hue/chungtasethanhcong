"""
Calendar Management Tools for OpenManus-Youtu Integrated Framework
Advanced calendar operations, scheduling, and reminder capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta, date, time
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

try:
    import icalendar
    from icalendar import Calendar, Event, Alarm
    CALENDAR_TOOLS_AVAILABLE = True
except ImportError:
    CALENDAR_TOOLS_AVAILABLE = False
    logger.warning("Calendar processing libraries not available. Install icalendar.")

class EventStatus(Enum):
    """Event status values."""
    TENTATIVE = "tentative"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class CalendarEvent:
    """Calendar event representation."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    start_datetime: datetime = field(default_factory=datetime.now)
    end_datetime: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    location: str = ""
    attendees: List[str] = field(default_factory=list)
    organizer: str = ""
    status: EventStatus = EventStatus.CONFIRMED
    priority: EventPriority = EventPriority.NORMAL
    is_all_day: bool = False
    recurrence_rule: Optional[str] = None
    reminders: List[int] = field(default_factory=list)  # Minutes before event
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CalendarReminder:
    """Calendar reminder representation."""
    reminder_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str = ""
    reminder_time: datetime = field(default_factory=datetime.now)
    message: str = ""
    is_sent: bool = False
    reminder_type: str = "notification"  # notification, email, sms
    created_at: datetime = field(default_factory=datetime.now)

class CalendarManager:
    """Advanced calendar management system."""
    
    def __init__(self):
        self.events: Dict[str, CalendarEvent] = {}
        self.reminders: Dict[str, CalendarReminder] = {}
        self.calendars: Dict[str, Dict[str, Any]] = {}
        self._reminder_task = None
        
        # Start reminder monitoring
        asyncio.create_task(self._monitor_reminders())
    
    def create_calendar(self, calendar_name: str, description: str = "", 
                       timezone: str = "UTC") -> str:
        """Create a new calendar."""
        calendar_id = str(uuid.uuid4())
        self.calendars[calendar_id] = {
            "id": calendar_id,
            "name": calendar_name,
            "description": description,
            "timezone": timezone,
            "created_at": datetime.now().isoformat(),
            "events": []
        }
        logger.info(f"Created calendar: {calendar_name}")
        return calendar_id
    
    def create_event(self, title: str, start_datetime: datetime, 
                    end_datetime: datetime = None, description: str = "",
                    location: str = "", attendees: List[str] = None,
                    calendar_id: str = None) -> str:
        """Create a new calendar event."""
        if end_datetime is None:
            end_datetime = start_datetime + timedelta(hours=1)
        
        event = CalendarEvent(
            title=title,
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            attendees=attendees or []
        )
        
        self.events[event.event_id] = event
        
        # Add to calendar if specified
        if calendar_id and calendar_id in self.calendars:
            self.calendars[calendar_id]["events"].append(event.event_id)
        
        logger.info(f"Created event: {title}")
        return event.event_id
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing event."""
        if event_id not in self.events:
            return False
        
        event = self.events[event_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        event.updated_at = datetime.now()
        logger.info(f"Updated event: {event_id}")
        return True
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        if event_id not in self.events:
            return False
        
        # Remove from calendars
        for calendar in self.calendars.values():
            if event_id in calendar["events"]:
                calendar["events"].remove(event_id)
        
        # Remove associated reminders
        reminders_to_remove = [r_id for r_id, reminder in self.reminders.items() 
                              if reminder.event_id == event_id]
        for r_id in reminders_to_remove:
            del self.reminders[r_id]
        
        del self.events[event_id]
        logger.info(f"Deleted event: {event_id}")
        return True
    
    def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """Get event by ID."""
        return self.events.get(event_id)
    
    def get_events_in_range(self, start_date: datetime, end_date: datetime,
                           calendar_id: str = None) -> List[CalendarEvent]:
        """Get events within date range."""
        events = []
        
        for event in self.events.values():
            # Check if event overlaps with range
            if (event.start_datetime <= end_date and event.end_datetime >= start_date):
                # Check calendar filter
                if calendar_id:
                    if calendar_id in self.calendars:
                        if event.event_id not in self.calendars[calendar_id]["events"]:
                            continue
                    else:
                        continue
                
                events.append(event)
        
        # Sort by start time
        events.sort(key=lambda e: e.start_datetime)
        return events
    
    def get_events_for_date(self, target_date: date, calendar_id: str = None) -> List[CalendarEvent]:
        """Get events for a specific date."""
        start_datetime = datetime.combine(target_date, time.min)
        end_datetime = datetime.combine(target_date, time.max)
        return self.get_events_in_range(start_datetime, end_datetime, calendar_id)
    
    def get_upcoming_events(self, hours_ahead: int = 24, calendar_id: str = None) -> List[CalendarEvent]:
        """Get upcoming events within specified hours."""
        now = datetime.now()
        future_time = now + timedelta(hours=hours_ahead)
        return self.get_events_in_range(now, future_time, calendar_id)
    
    def add_reminder(self, event_id: str, minutes_before: int, 
                    message: str = "", reminder_type: str = "notification") -> str:
        """Add reminder to an event."""
        if event_id not in self.events:
            return None
        
        event = self.events[event_id]
        reminder_time = event.start_datetime - timedelta(minutes=minutes_before)
        
        reminder = CalendarReminder(
            event_id=event_id,
            reminder_time=reminder_time,
            message=message or f"Reminder: {event.title}",
            reminder_type=reminder_type
        )
        
        self.reminders[reminder.reminder_id] = reminder
        logger.info(f"Added reminder for event: {event_id}")
        return reminder.reminder_id
    
    def create_recurring_event(self, title: str, start_datetime: datetime,
                              end_datetime: datetime, recurrence_rule: str,
                              end_recurrence: datetime = None) -> str:
        """Create recurring event."""
        event = CalendarEvent(
            title=title,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            recurrence_rule=recurrence_rule
        )
        
        self.events[event.event_id] = event
        
        # Generate recurring instances
        if end_recurrence:
            self._generate_recurring_instances(event, end_recurrence)
        
        logger.info(f"Created recurring event: {title}")
        return event.event_id
    
    def _generate_recurring_instances(self, base_event: CalendarEvent, end_date: datetime) -> None:
        """Generate instances of recurring event."""
        # Simple daily recurrence for now (can be enhanced)
        if "DAILY" in base_event.recurrence_rule:
            current_date = base_event.start_datetime + timedelta(days=1)
            while current_date <= end_date:
                instance = CalendarEvent(
                    title=base_event.title,
                    description=base_event.description,
                    start_datetime=current_date,
                    end_datetime=current_date + (base_event.end_datetime - base_event.start_datetime),
                    location=base_event.location,
                    attendees=base_event.attendees.copy(),
                    recurrence_rule=base_event.recurrence_rule,
                    metadata={"parent_event_id": base_event.event_id}
                )
                self.events[instance.event_id] = instance
                current_date += timedelta(days=1)
    
    async def _monitor_reminders(self) -> None:
        """Monitor and trigger reminders."""
        while True:
            try:
                now = datetime.now()
                triggered_reminders = []
                
                for reminder_id, reminder in self.reminders.items():
                    if not reminder.is_sent and reminder.reminder_time <= now:
                        triggered_reminders.append(reminder)
                
                # Process triggered reminders
                for reminder in triggered_reminders:
                    await self._process_reminder(reminder)
                    reminder.is_sent = True
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Reminder monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _process_reminder(self, reminder: CalendarReminder) -> None:
        """Process a triggered reminder."""
        try:
            event = self.events.get(reminder.event_id)
            if not event:
                return
            
            # Log reminder (can be enhanced to send notifications, emails, etc.)
            logger.info(f"REMINDER: {reminder.message}")
            logger.info(f"Event: {event.title}")
            logger.info(f"Start: {event.start_datetime}")
            logger.info(f"Location: {event.location}")
            
            # Here you could integrate with notification systems, email, etc.
            
        except Exception as e:
            logger.error(f"Failed to process reminder: {e}")
    
    def export_to_ical(self, calendar_id: str = None, events: List[str] = None) -> str:
        """Export events to iCalendar format."""
        if not CALENDAR_TOOLS_AVAILABLE:
            return ""
        
        try:
            cal = Calendar()
            cal.add('prodid', '-//OpenManus-Youtu Framework//Calendar//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            
            # Determine which events to export
            if events:
                event_ids = events
            elif calendar_id and calendar_id in self.calendars:
                event_ids = self.calendars[calendar_id]["events"]
            else:
                event_ids = list(self.events.keys())
            
            for event_id in event_ids:
                if event_id in self.events:
                    event = self.events[event_id]
                    
                    ical_event = Event()
                    ical_event.add('uid', event.event_id)
                    ical_event.add('summary', event.title)
                    ical_event.add('description', event.description)
                    ical_event.add('location', event.location)
                    ical_event.add('dtstart', event.start_datetime)
                    ical_event.add('dtend', event.end_datetime)
                    ical_event.add('status', event.status.value.upper())
                    ical_event.add('created', event.created_at)
                    ical_event.add('last-modified', event.updated_at)
                    
                    # Add attendees
                    for attendee in event.attendees:
                        ical_event.add('attendee', attendee)
                    
                    # Add reminders
                    for reminder_minutes in event.reminders:
                        alarm = Alarm()
                        alarm.add('action', 'DISPLAY')
                        alarm.add('description', f'Reminder: {event.title}')
                        alarm.add('trigger', timedelta(minutes=-reminder_minutes))
                        ical_event.add_component(alarm)
                    
                    cal.add_component(ical_event)
            
            return cal.to_ical().decode('utf-8')
            
        except Exception as e:
            logger.error(f"iCalendar export failed: {e}")
            return ""
    
    def import_from_ical(self, ical_data: str) -> Dict[str, Any]:
        """Import events from iCalendar format."""
        if not CALENDAR_TOOLS_AVAILABLE:
            return {"error": "iCalendar library not available"}
        
        try:
            cal = Calendar.from_ical(ical_data)
            imported_events = []
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event = CalendarEvent(
                        event_id=component.get('uid', str(uuid.uuid4())),
                        title=component.get('summary', ''),
                        description=component.get('description', ''),
                        start_datetime=component.get('dtstart').dt if component.get('dtstart') else datetime.now(),
                        end_datetime=component.get('dtend').dt if component.get('dtend') else datetime.now() + timedelta(hours=1),
                        location=component.get('location', ''),
                        status=EventStatus(component.get('status', 'confirmed').lower()),
                        created_at=component.get('created').dt if component.get('created') else datetime.now(),
                        updated_at=component.get('last-modified').dt if component.get('last-modified') else datetime.now()
                    )
                    
                    # Extract attendees
                    attendees = []
                    for attendee in component.get('attendee', []):
                        if isinstance(attendee, str):
                            attendees.append(attendee)
                        else:
                            attendees.append(str(attendee))
                    event.attendees = attendees
                    
                    self.events[event.event_id] = event
                    imported_events.append(event.event_id)
            
            return {
                "success": True,
                "imported_events": len(imported_events),
                "event_ids": imported_events
            }
            
        except Exception as e:
            logger.error(f"iCalendar import failed: {e}")
            return {"error": str(e)}
    
    def get_calendar_statistics(self) -> Dict[str, Any]:
        """Get calendar system statistics."""
        return {
            "total_events": len(self.events),
            "total_reminders": len(self.reminders),
            "total_calendars": len(self.calendars),
            "upcoming_events": len(self.get_upcoming_events()),
            "pending_reminders": len([r for r in self.reminders.values() if not r.is_sent]),
            "events_by_status": {
                status.value: len([e for e in self.events.values() if e.status == status])
                for status in EventStatus
            },
            "events_by_priority": {
                priority.value: len([e for e in self.events.values() if e.priority == priority])
                for priority in EventPriority
            }
        }

# Global calendar manager instance
calendar_manager = CalendarManager()

# Convenience functions
def create_calendar_event(title: str, start_datetime: datetime, 
                         end_datetime: datetime = None, description: str = "") -> str:
    """Create a calendar event."""
    return calendar_manager.create_event(title, start_datetime, end_datetime, description)

def get_events_for_today(calendar_id: str = None) -> List[CalendarEvent]:
    """Get events for today."""
    return calendar_manager.get_events_for_date(date.today(), calendar_id)

def get_upcoming_events(hours_ahead: int = 24) -> List[CalendarEvent]:
    """Get upcoming events."""
    return calendar_manager.get_upcoming_events(hours_ahead)

def add_event_reminder(event_id: str, minutes_before: int, message: str = "") -> str:
    """Add reminder to event."""
    return calendar_manager.add_reminder(event_id, minutes_before, message)

def export_calendar_to_ical(calendar_id: str = None) -> str:
    """Export calendar to iCalendar format."""
    return calendar_manager.export_to_ical(calendar_id)

def import_calendar_from_ical(ical_data: str) -> Dict[str, Any]:
    """Import calendar from iCalendar format."""
    return calendar_manager.import_from_ical(ical_data)