from datetime import datetime, timedelta

# Assuming `tickets` is a collection of ticket records with fields `priority` and `create_date`

# Define time thresholds for each priority level
priority_thresholds = {
    'minimal': timedelta(days=2),
    'moderate': timedelta(days=1),
    'critical': timedelta(hours=2)
}

# Initialize dictionaries to store total time and count of tickets for each priority level
total_time = {priority: timedelta() for priority in priority_thresholds}
ticket_count = {priority: 0 for priority in priority_thresholds}

# Calculate total time and count of tickets for each priority level
for ticket in tickets:
    priority = ticket.priority
    time_taken = datetime.now() - ticket.create_date  # Calculate time taken based on current date
    total_time[priority] += time_taken
    ticket_count[priority] += 1

# Calculate average time taken for each priority level
average_time = {priority: total_time[priority] / ticket_count[priority] if ticket_count[priority] else timedelta() for priority in priority_thresholds}

print(average_time)