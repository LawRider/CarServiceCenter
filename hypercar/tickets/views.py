from collections import deque
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView

line_of_cars = {
    'change_oil': deque(),
    'inflate_tires': deque(),
    'diagnostic': deque(),
}
count_ticket_id = 0
next_ticket_id = 0


class MenuView(TemplateView):
    template_name = 'tickets/menu.html'
    entries = {"change_oil": "Change oil",
               "inflate_tires": "Inflate tires",
               "diagnostic": "Get diagnostic test"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entries'] = self.entries
        return context


class TicketView(View):
    def get(self, request, link, *args, **kwargs):
        ticket_id = self.get_ticket_id()
        tickets = line_of_cars[link]
        num_tickets = len(tickets)
        tickets.append(ticket_id)
        waiting_time = self.count_time(num_tickets, link)
        return render(request, 'tickets/' + link + '.html',
                      {'id': ticket_id, 'time': waiting_time})

    @staticmethod
    def get_ticket_id():
        global count_ticket_id
        count_ticket_id += 1
        return count_ticket_id

    @staticmethod
    def count_time(num, service):
        if service == 'change_oil':
            waiting_time = 2 * num
        elif service == 'inflate_tires':
            wait_extra = 2 * len(line_of_cars['change_oil'])
            waiting_time = 5 * num + wait_extra
        else:
            wait_extra = 2 * len(line_of_cars['change_oil']) + \
                         5 * len(line_of_cars['inflate_tires'])
            waiting_time = 30 * num + wait_extra
        return waiting_time


class ProcessingView(View):
    def get(self, request, *args, **kwargs):
        queues = [len(v) for v in line_of_cars.values()]
        return render(request, 'tickets/processing.html', {'queues': queues})

    def post(self, request, *args, **kwargs):
        global next_ticket_id
        if line_of_cars['change_oil']:
            next_ticket_id = line_of_cars['change_oil'].popleft()
        elif line_of_cars['inflate_tires']:
            next_ticket_id = line_of_cars['inflate_tires'].popleft()
        elif line_of_cars['diagnostic']:
            next_ticket_id = line_of_cars['diagnostic'].popleft()
        return redirect('/next/')


class NextView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/next.html', {'id': next_ticket_id})
