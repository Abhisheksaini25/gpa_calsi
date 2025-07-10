from django.shortcuts import render
from django.http import JsonResponse
from supabase import create_client
from django.conf import settings

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def home(request):
    return render(request, 'home.html')

def save_history(target, total, remaining, current, required):
    try:
        supabase.table('Gpa_history').insert({
            'target_gpa': target,
            'total_sems': total,
            'remaining_sems': remaining,
            'current_gpa': current,
            'required_gpa': required
        }).execute()
    except Exception as e:
        print("Supabase save failed:", e)

def calculate_gpa(request):
    if request.method == 'POST':
        try:
            target_gpa = float(request.POST.get('target_gpa', 0))
            total_sems = int(request.POST.get('total_sems', 0))
            current_sem = int(request.POST.get('remaining_sems', 0))
            current_gpa = float(request.POST.get('current_gpa', 0))

            if current_sem > total_sems:
                return JsonResponse({'result': 'No semesters left to improve GPA.'})

            remaining_sems = total_sems - current_sem + 1
            completed_sems = total_sems - remaining_sems
            total_required_points = target_gpa * total_sems
            current_points = current_gpa * completed_sems
            needed_points = total_required_points - current_points
            required_avg = needed_points / remaining_sems

            if required_avg > 10:
                return JsonResponse({'result': 'Not possible to achieve the target GPA.'})

            required_avg = round(required_avg, 2)

            # Save only valid entries
            save_history(target_gpa, total_sems, remaining_sems, current_gpa, required_avg)

            return JsonResponse({'result': required_avg})

        except Exception as e:
            print("Error:", e)
            return JsonResponse({'result': 'Invalid input.'})

    return JsonResponse({'result': 'Invalid request method.'})
