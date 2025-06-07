import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from matplotlib import pyplot as plt
from .form import MyForm
import os
from django.conf import settings
from django.http import HttpResponse
from .form import TeacherRegistrationForm, studentmakeform, UploadCSVForm
from django.shortcuts import render
from .models import StudentMark
from .form import EditStudentForm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# Your view logic


student_file_path = os.path.join(settings.BASE_DIR, 'students.csv')
teacher_file_path = os.path.join(settings.BASE_DIR, 'teachers.csv')

def submit_form(request):
    if request.method == 'POST':
        form = MyForm(request.POST)

        if form.is_valid():
            submit_type = request.POST.get('submitType')
            user_type = form.cleaned_data['user_type']
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            student_id = form.cleaned_data['student_id']
            cohort = form.cleaned_data['cohort']
            subjects = form.cleaned_data.get('subjects', '')  # New field for subjects
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if submit_type == 'student':
                # Check for duplicate student
                student_exists = False
                try:
                    with open(student_file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            if row[2] == student_id:
                                student_exists = True
                                break
                except FileNotFoundError:
                    pass  # If the file doesn't exist, we can proceed to create it
                
                if student_exists:
                    messages.error(request, "Student is already registered.")
                    return redirect('/view/')
                
                # Save student data to CSV
                with open(student_file_path, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([name, last_name, student_id, cohort, subjects])  # Include subjects
                messages.success(request, "Student registered successfully!")
                return redirect('/view/')

            
            elif submit_type == 'teacher':
                # Check for duplicate teacher
                teacher_exists = False
                try:
                    with open(teacher_file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            if row[0] == username:
                                teacher_exists = True
                                break
                except FileNotFoundError:
                    pass  # If the file doesn't exist, we can proceed to create it
                
                if teacher_exists:
                    messages.error(request, "Teacher is already registered.")
                    return redirect('/teachers/')
                
                # Save teacher data to CSV
                with open(teacher_file_path, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([username, password])
                messages.success(request, "Teacher registered successfully!")
                return redirect('/teachers/')
            
    else:
        form = MyForm()
    return render(request, 'login.html', {'form': form})

def view_csv(request):
    data = []
    try:
        with open(student_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)  # Convert the reader object to a list of rows
    except FileNotFoundError:
        messages.error(request, "CSV file not found.")
    except IOError:
        messages.error(request, "Error reading the file.")
    
    return render(request, 'view.html', {'data': data})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Check for duplicate teacher
            teacher_exists = False
            try:
                with open(teacher_file_path, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if row[0] == username:
                            teacher_exists = True
                            break
            except FileNotFoundError:
                pass  # If the file doesn't exist, we can proceed to create it
            
            if teacher_exists:
                messages.error(request, "Teacher is already registered.")
                return redirect('/login/')
            
            # Save teacher data to CSV
            with open(teacher_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([username, password])
            messages.success(request, "Teacher registered successfully!")
            
            return redirect('teachers_page')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'register_teacher.html', {'form': form})
def teachers_page(request):
    return render(request, 'teachers.html')

def home_page(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contract.html')

def log_in_out(request):
    logout(request)
    return redirect('/login/')

def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        studentid = request.POST.get('studentid')
        module = request.POST.get('module')
        
        # Check if a user with the provided student ID already exists
        if User.objects.filter(username=studentid).exists():
            messages.info(request, "Student is already registered.")
            return redirect('/register/')
        
        # Create a new User object
        try:
            user = User.objects.create_user(
                username=studentid,  # Use studentid as username
                first_name=first_name,
                last_name=last_name,
                password=None  # Set password to None or handle it as needed
            )
            user.save()
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect('/register/')
        
        # Append the new user data to a CSV file
        with open(student_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([first_name, last_name, studentid, module])
        
        messages.info(request, "Account created successfully!")
        return redirect('/register/')
    
    return render(request, 'resgis.html')

def mark(request):
    data = []
    try:
        with open(student_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)  # Convert the reader object to a list of rows
    except FileNotFoundError:
        messages.error(request, "CSV file not found.")
    except IOError:
        messages.error(request, "Error reading the file.")
    
    return render(request, 'marking.html', {'data': data})

def studentmark(request):
    
    if request.method == 'POST':
        form = studentmakeform(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            student_id = form.cleaned_data['student_id']
            cohort = form.cleaned_data['cohort']
            Computer_Arquitecture = form.cleaned_data['Computer_Arquitecture']
            Networking = form.cleaned_data['Networking']
            R_Programming = form.cleaned_data['R_Programming']
            
            # Save student data to CSV
            with open(student_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([name, last_name, student_id, cohort, Computer_Arquitecture, Networking, R_Programming])
            messages.success(request, "Student registered successfully!")
            return redirect('/mark/')
    else:
        form = studentmakeform()
            
    return render(request, 'studentmake.html', {'form': form})
 # Update with your actual path

def teachers_page(request):
    student_count = 0
    cohort_count = 0
    students = []
    cohorts = set()  # Use a set to collect unique cohorts

    try:
        with open(student_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            students = list(reader)
            student_count = len(students)
            for row in students:
                if len(row) > 3:  # Assuming cohort is in the 4th column
                    cohorts.add(row[3])
            cohort_count = len(cohorts)  # Count the number of unique cohorts
    except FileNotFoundError:
        messages.error(request, "CSV file not found.")
    except IOError:
        messages.error(request, "Error reading the file.")
    
    return render(request, 'teachers.html', {'student_count': student_count, 'students': students, 'cohort_count': cohort_count, 'cohorts': list(cohorts)})







def edit_student(request, student_id):
    student_data = None
    try:
        with open(student_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[2] == student_id:
                    student_data = row
                    break
    except FileNotFoundError:
        messages.error(request, "CSV file not found.")
        return redirect('teachers')
    except IOError:
        messages.error(request, "Error reading the file.")
        return redirect('teachers')

    if not student_data:
        messages.error(request, "Student not found.")
        return redirect('teachers')

    if request.method == 'POST':
        form = EditStudentForm(request.POST)
        if form.is_valid():
            updated_data = [
                form.cleaned_data['name'],
                form.cleaned_data['last_name'],
                form.cleaned_data['student_id'],
                form.cleaned_data['cohort'],
                form.cleaned_data['Computer_Arquitecture'],
                form.cleaned_data['Networking'],
                form.cleaned_data['R_Programming']
            ]

            # Update CSV
            all_students = []
            with open(student_file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row[2] == student_id:
                        all_students.append(updated_data)
                    else:
                        all_students.append(row)

            with open(student_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(all_students)

            messages.success(request, "Student information updated successfully!")
            return redirect('teachers')
    else:
        form = EditStudentForm(initial={
            'name': student_data[0],
            'last_name': student_data[1],
            'student_id': student_data[2],
            'cohort': student_data[3],
            'Computer_Arquitecture': student_data[4],
            'Networking': student_data[5],
            'R_Programming': student_data[6]
        })

    return render(request, 'edit_student.html', {'form': form, 'student_id': student_id})



from django.http import JsonResponse
import csv
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string


def search_csv(request):
    # Define the path to the CSV file
    student_file_path = settings.BASE_DIR / 'data/students.csv'
    data = []

    if request.method == 'POST':
        # Handle form submission to edit CSV data
        updated_data = request.POST.getlist('data')
        rows = [row.split(',') for row in updated_data]
        try:
            with open(student_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
            messages.success(request, "CSV file updated successfully!")
        except IOError:
            messages.error(request, "Error writing to the file.")
        return redirect('search_csv')

    try:
        # Read data from CSV
        with open(student_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
    except FileNotFoundError:
        messages.error(request, "CSV file not found.")
    except IOError:
        messages.error(request, "Error reading the file.")

    return render(request, 'marking.html', {'data': data})


from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.contrib import messages

# Path to your CSV file


student_file_path = "C:/Users/HP/Desktop/monopoly sub/registration/students.csv"

def searchs(request):
    query = request.GET.get('q', '').strip()  # Get and strip the search query
    results = []

    try:
        with open(student_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
            if query:
                results = [row for row in data if (query.lower() in row[0].lower() or query.lower() in row[2].lower())]
            else:
                results = data  # Display all data if no query
    except FileNotFoundError:
        messages.error(request, "CSV file not found.")
    except IOError:
        messages.error(request, "Error reading the file.")

    return render(request, 'view.html', {'query': query, 'results': results})






from django.shortcuts import render, redirect, HttpResponse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                return HttpResponse("Please upload a CSV file.")
            
            # Read and process the CSV file
            file_data = csv_file.read().decode("utf-8")
            lines = file_data.split("\n")
            
            students_data = []
            for line in lines[1:]:  # Skip header
                fields = line.strip().split(",")
                if len(fields) >= 7:  # Ensure there are enough columns
                    students_data.append(fields)
            
            # Store data in session
            request.session['students_data'] = students_data
            return redirect('show_graph')
    else:
        form = UploadCSVForm()
    
    return render(request, 'upload_csv.html', {'form': form})

def show_graph(request):
    # Retrieve data from session
    students_data = request.session.get('students_data', [])
    
    if not students_data:
        return HttpResponse("No student data available. Please upload a CSV file first.")

    # Calculate cohort averages
    cohorts = {}
    for row in students_data:
        try:
            cohort = row[3]
            comp_arch = float(row[4])
            networking = float(row[5])
            r_programming = float(row[6])
        except (IndexError, ValueError) as e:
            return HttpResponse(f"Error processing data: {e}")

        if cohort not in cohorts:
            cohorts[cohort] = {
                'students': 0,
                'Comp Arch': 0.0,
                'Networking': 0.0,
                'R Programming': 0.0
            }

        cohorts[cohort]['students'] += 1
        cohorts[cohort]['Comp Arch'] += comp_arch
        cohorts[cohort]['Networking'] += networking
        cohorts[cohort]['R Programming'] += r_programming

    # Prepare data for plotting
    labels = []
    ca_marks = []
    net_marks = []
    rp_marks = []

    for cohort, data in cohorts.items():
        labels.append(cohort)
        ca_marks.append(data['Comp Arch'] / data['students'])
        net_marks.append(data['Networking'] / data['students'])
        rp_marks.append(data['R Programming'] / data['students'])

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(labels))
    
    ax.bar(x, ca_marks, width=0.2, label='Comp Arch', align='center')
    ax.bar([p + 0.2 for p in x], net_marks, width=0.2, label='Networking', align='center')
    ax.bar([p + 0.4 for p in x], rp_marks, width=0.2, label='R Programming', align='center')

    ax.set_xticks([p + 0.2 for p in x])
    ax.set_xticklabels(labels)
    ax.set_xlabel('Cohorts')
    ax.set_ylabel('Average Marks')
    ax.set_title('Average Marks per Subject by Cohort')
    ax.legend()

    # Save plot to response
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    plt.close(fig)
    
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Length'] = str(len(response.content))
    return response