
# This is the main file of the project.
#   But you can add as many files as you want.
#-----------------------------------------

#################################
#  Start writing your code here:
#################################
# Info About how files are read:
# Passengers are first registered using normal seat reservation method/button
# Their data can be saved onto a file called "registered.txt" by clicking on Save to a file button
# Later on, if seat reservation of that passenger is cancelled, it can be retrieved from registered.txt file by clicking the load from a file button 
# And thus, their seat can be reserved from that very file





import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, Frame, Label


#Manages the amin window and widgets/labels/buttons/listboxes in it
class SeatReservationSystem(tk.Tk):
    def __init__(self, management):
        super().__init__()
        self.management = management
        self.title("PIA Airline Reservation")
        self.terroristData = self.loadTerroristData() # Load terrorist data from a super secret file :
        self.createWidgets()

    # Responsible for creating the main menu and button's functionality
    def createWidgets(self):
        self.mainFrame = Frame(self)
        self.mainFrame.pack(pady=20)
        self.geometry("600x550")

        self.titleLabel = Label(self.mainFrame, text="PIA Ticket Reservation", font=("Helvetica", 16))
        self.titleLabel.grid(row=0, column=0, columnspan=3, pady=10)

        self.addPlaneButton = tk.Button(self.mainFrame, text="Add new Plane", command=self.addNewPlane)
        self.addPlaneButton.grid(row=1, column=0, columnspan=3, pady=5)

        self.planeVar = tk.StringVar(self)
        self.planeVar.set("Plane 1")
        self.planeVar.trace("w", self.onPlaneSelect)

        self.planeMenu = tk.OptionMenu(self.mainFrame, self.planeVar, *self.getPlaneNames())
        self.planeMenu.grid(row=2, column=0, columnspan=3, pady=5)

        self.reserveButton = tk.Button(self.mainFrame, text="Seat Reservation", command=self.openReserveSeatWindow)
        self.reserveButton.grid(row=3, column=0, columnspan=3, pady=5)

        self.cancelButton = tk.Button(self.mainFrame, text="Seat Cancellation", command=self.openCancelReservationWindow)
        self.cancelButton.grid(row=4, column=0, columnspan=3, pady=5)

        self.loadButton = tk.Button(self.mainFrame, text="Load from File", command=self.loadFromFile)
        self.loadButton.grid(row=5, column=0, columnspan=3, pady=5)

        self.saveButton = tk.Button(self.mainFrame, text="Save to File", command=self.saveToFile)
        self.saveButton.grid(row=6, column=0, columnspan=3, pady=5)

        self.businessClassListbox = self.createListbox(self.mainFrame, "Business Class", 0)
        self.economyClassListbox = self.createListbox(self.mainFrame, "Economy Class", 1)
        self.studentClassListbox = self.createListbox(self.mainFrame, "Student Class", 2)

        self.planButton = tk.Button(self.mainFrame, text="Show Seating Plan", command=self.showSeatingPlan)
        self.planButton.grid(row=8, column=0, columnspan=3, pady=10)

    # Creates the listbox for displaying the passengers name on main menu
    def createListbox(self, parent, label, column):
        listFrame = Frame(parent)
        listFrame.grid(row=7, column=column, padx=10)
        listLabel = Label(master = listFrame, text=label, font=("Helvetica", 12), fg="blue")
        listLabel.pack()
        listbox = Listbox(master = listFrame, width=20, height=10)
        listbox.pack(side="left", fill="y")
        scrollbar = Scrollbar(master = listFrame, orient="vertical")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        listbox.bind('<<ListboxSelect>>', self.onListboxSelect)
        return listbox

    # Refreshes the listboxes for passengers to be entered
    def refreshSeatListboxes(self):
        self.businessClassListbox.delete(0, tk.END)
        self.economyClassListbox.delete(0, tk.END)
        self.studentClassListbox.delete(0, tk.END)

        currentPlane = self.management.getCurrentPlane()

        for passenger in currentPlane.passengers:
            if passenger.seatClass == "business":
                self.businessClassListbox.insert(tk.END, passenger.name)
            elif passenger.seatClass == "economy":
                self.economyClassListbox.insert(tk.END, passenger.name)
            elif passenger.seatClass == "student":
                self.studentClassListbox.insert(tk.END, passenger.name)

    def openReserveSeatWindow(self):
        ReserveSeatWindow(self, self.management.getCurrentPlane())

    def openCancelReservationWindow(self):
        CancelReservationWindow(self, self.management.getCurrentPlane())

    # Retreives data from a file to load into the reservations system
    def loadFromFile(self):
        try:
            with open("registered.txt", "r") as f:
                currentPlane = self.management.getCurrentPlane()
                currentPlane.passengers = []
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 5:
                        name, passengerId, seatClass, seatNumber, luggage = parts
                        seatNumber = int(seatNumber)
                        luggage = int(luggage)
                        newPassenger = Passenger(name, passengerId, seatClass, seatNumber, luggage)
                        seatingClass = currentPlane.getSeatingClass(seatClass)
                        if seatingClass:
                            if seatNumber >= 1 and seatNumber <= seatingClass.totalSeats:
                                seatingClass.seats[seatNumber - 1].passenger = newPassenger
                                currentPlane.passengers.append(newPassenger)
                                currentPlane.currentCargo += luggage
                self.refreshSeatListboxes()
                
                messagebox.showinfo("Success", "Data loaded successfully.")
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Saves data to a file of those who have been registered already
    def saveToFile(self):
        try:
            with open("registered.txt", "w") as f:
                currentPlane = self.management.getCurrentPlane()
                for passenger in currentPlane.passengers:
                    f.write(f"{passenger.name},{passenger.passengerId},{passenger.seatClass},{passenger.seatNumber},{passenger.luggage}\n")
                messagebox.showinfo("Success", "Data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    #Reads data from a file to identify terrorists
    def loadTerroristData(self):
        data = {}
        try:
            with open("isidata.txt", "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        data[parts[0]] = parts[1]
        except FileNotFoundError:
            messagebox.showerror("Error", "Terrorist data file not found.")
        return data

    def showSeatingPlan(self):
        SeatingPlanWindow(self, self.management.getCurrentPlane(), self.terroristData)
    
    # On selection of passenger in Listbox
    def onListboxSelect(self, event):
        selectedListbox = event.widget
        selectedI = selectedListbox.curselection()
        if selectedI:
            selectedI = selectedI[0]
            name = selectedListbox.get(selectedI)
            currentPlane = self.management.getCurrentPlane()
            for passenger in currentPlane.passengers:
                if passenger.name == name:
                    passenger_info = f"Name: {passenger.name}\nID: {passenger.passengerId}\nClass: {passenger.seatClass}\nSeat: {passenger.seatNumber}\nLuggage: {passenger.luggage}"
                    messagebox.showinfo("Passenger Information", passenger_info)
                    break

    # Option to add new plane
    def addNewPlane(self):
        self.management.addPlane()
        self.planeMenu['menu'].add_command(label=f"Plane {len(self.management.planes)}", command=tk._setit(self.planeVar, f"Plane {len(self.management.planes)}"))

    def getPlaneNames(self):
        planeNames = []  # Initialize an empty list to store the plane names
        for i in range(len(self.management.planes)): 
            planeName = "Plane " + str(i + 1)  
            planeNames.append(planeName)  
        return planeNames  

    # Updates the current plane based on the user’s selection from a dropdown menu
    def onPlaneSelect(self, *args):
        selectedPlane = self.planeVar.get()
        if selectedPlane.startswith("Plane "):
            planeIndex = int(selectedPlane.split(" ")[1]) - 1
            self.management.setCurrentPlane(planeIndex)
            self.refreshSeatListboxes()


class SeatingClass:
    def __init__(self, classType, seatsPerRow, totalSeats, pricePerSeat):
        self.classType = classType
        self.seatsPerRow = seatsPerRow
        self.totalSeats = totalSeats
        self.pricePerSeat = pricePerSeat
        self.seats = []
        for i in range(totalSeats):
            self.seats.append(Seat(i + 1))


class Plane:
    def __init__(self):
        self.businessClass = SeatingClass("business", 4, 12, 200000)
        self.economyClass = SeatingClass("economy", 4, 24, 100000)
        self.studentClass = SeatingClass("student", 4, 8, 40000)
        self.passengers = []
        self.cargoCapacity = 2000 # Maximum cargo capacity in kg
        self.currentCargo = 0 # Current cargo load

    def addPassenger(self, passenger):
        # Check if adding the passenger's luggage exceeds the cargo capacity
        if self.currentCargo + passenger.luggage <= self.cargoCapacity:
            self.passengers.append(passenger)
            self.currentCargo += passenger.luggage
            return True # Passenger added successfully
        return False # Adding passenger failed due to cargo capacity being exceeded

    def getSeatingClass(self, seatClass):
        if seatClass == "business":
            return self.businessClass
        elif seatClass == "economy":
            return self.economyClass
        elif seatClass == "student":
            return self.studentClass
        return None


class Passenger:
    def __init__(self, name, passengerId, seatClass, seatNumber, luggage):
        self.name = name
        self.passengerId = passengerId
        self.seatClass = seatClass
        self.seatNumber = seatNumber
        self.luggage = luggage


class Seat:
    def __init__(self, number):
        self.number = number
        self.passenger = None


class PIAManagement:
    def __init__(self):
        self.planes = [Plane()]
        self.currentPlaneIndex = 0

    def addPlane(self):
        self.planes.append(Plane())

    def getCurrentPlane(self):
        return self.planes[self.currentPlaneIndex]

    def setCurrentPlane(self, index):
        self.currentPlaneIndex = index


# Responsible for reserving passengers
class ReserveSeatWindow(tk.Toplevel):
    def __init__(self, parent, plane):
        super().__init__(parent)
        self.parent = parent
        self.plane = plane
        self.title("Reserve Seat")
        self.geometry("225x175")
        self.createWidgets()

    # Creates and arranges the widgets for the reservation window.
    def createWidgets(self):
        Label(self, text="Passenger Name:").grid(row=0, column=0)
        self.nameEntry = tk.Entry(self)
        self.nameEntry.grid(row=0, column=1)

        Label(self, text="Passenger ID:").grid(row=1, column=0)
        self.idEntry = tk.Entry(self)
        self.idEntry.grid(row=1, column=1)

        Label(self, text="Seat Class:").grid(row=2, column=0)
        self.classVar = tk.StringVar(self)
        self.classVar.set("business")
        tk.OptionMenu(self, self.classVar, "business", "economy", "student").grid(row=2, column=1)

        Label(self, text="Seat Number:").grid(row=3, column=0)
        self.seatNumberEntry = tk.Entry(self)
        self.seatNumberEntry.grid(row=3, column=1)

        Label(self, text="Luggage Weight:").grid(row=4, column=0)
        self.luggageEntry = tk.Entry(self)
        self.luggageEntry.grid(row=4, column=1)

        self.reserveButton = tk.Button(self, text="Reserve", command=self.reserveSeat)
        self.reserveButton.grid(row=5, column=0, columnspan=2, pady=10)

    # Validates input, checks seat availability and adds the passenger if all checks pass
    def reserveSeat(self):
        name = self.nameEntry.get()
        passengerId = self.idEntry.get()
        seatClass = self.classVar.get()
        try:
            seatNumber = int(self.seatNumberEntry.get())
            luggage = int(self.luggageEntry.get())
        except ValueError:
            messagebox.showerror("Error", "Seat Number and Luggage Weight must be integers.")
            return
        if luggage > 100:
            messagebox.showerror("Error", "Luggage weight exceeds the maximum limit of 100 kg.")
            return

        seatingClass = self.plane.getSeatingClass(seatClass)
        if seatingClass:
            if seatNumber >= 1 and seatNumber <= seatingClass.totalSeats:
                if seatingClass.seats[seatNumber - 1].passenger is None:
                    newPassenger = Passenger(name, passengerId, seatClass, seatNumber, luggage)
                    if self.plane.addPassenger(newPassenger):
                        seatingClass.seats[seatNumber - 1].passenger = newPassenger
                        self.parent.refreshSeatListboxes()
                        messagebox.showinfo("Success", "Seat reserved successfully.")
                        self.destroy()
                    else:
                        messagebox.showerror("Error", "Cargo capacity exceeded. Cannot add more luggage.")
                else:
                    messagebox.showerror("Error", "Seat already taken.")
            else:
                messagebox.showerror("Error", "Invalid seat number.")
        else:
            messagebox.showerror("Error", "Invalid class.")

# Responsible for cancelling reservation of passengers according to the Passenegr ID
class CancelReservationWindow(tk.Toplevel):
    def __init__(self, parent, plane):
        super().__init__(parent)
        self.parent = parent
        self.plane = plane
        self.title("Cancel Reservation")
        self.geometry("300x150")
        self.createWidgets()
    
    def createWidgets(self):
        Label(self, text="Passenger ID:").grid(row=0, column=0, padx=10, pady=10)
        self.idEntry = tk.Entry(self)
        self.idEntry.grid(row=0, column=1, padx=10, pady=10)
        self.cancelButton = tk.Button(self, text="Cancel Reservation", command=self.cancelReservation)
        self.cancelButton.grid(row=1, column=0, columnspan=2, pady=10)

    # Responsible for cancelling reservation according to the PassengerID
    def cancelReservation(self):
        passengerId = self.idEntry.get()
        currentPlane = self.plane

        for passenger in currentPlane.passengers:
            if passenger.passengerId == passengerId:
                seatingClass = currentPlane.getSeatingClass(passenger.seatClass)
                if seatingClass:
                    seatingClass.seats[passenger.seatNumber - 1].passenger = None
                currentPlane.passengers.remove(passenger)
                currentPlane.currentCargo -= passenger.luggage
                self.parent.refreshSeatListboxes()
                messagebox.showinfo("Success", "Reservation cancelled successfully.")
                self.destroy()
                return
        messagebox.showerror("Error", "Passenger not found.")


# Manages seating plan widgets
class SeatingPlanWindow(tk.Toplevel):
    def __init__(self, parent, plane, terroristData, highlightPassenger=None):
        super().__init__(parent)
        self.plane = plane
        self.terroristData = terroristData
        self.highlightPassenger = highlightPassenger
        self.title("Seating Plan")
        self.createWidgets()
       
    # This window shows the state of the plane
    def createWidgets(self):
        self.seatButtons = {}
        classes = [self.plane.businessClass, self.plane.economyClass, self.plane.studentClass]
        classNames = ["Business Class", "Economy Class", "Student Class"]
        row = 0

        for classI, seatingClass in enumerate(classes):
            classLabel = tk.Label(self, text=classNames[classI], font=("Arial", 15, "bold"), fg="lightblue", bg="black")
            classLabel.grid(row=row, column=0, columnspan=seatingClass.seatsPerRow, pady=5)
            row += 1

            for i in range(len(seatingClass.seats)):
                seat = seatingClass.seats[i]
                button = tk.Button(self, text=str(seat.number), state="disabled")
                row_index = row + (seat.number - 1) // seatingClass.seatsPerRow
                column_index = (seat.number - 1) % seatingClass.seatsPerRow
                button.grid(row=row_index, column=column_index, padx=5, pady=5)
                self.seatButtons[seat.number] = button
                
                # Highlights passenger's seat according to Passenger ID in isidata.txt
                if seat.passenger:
                    if self.terroristData.get(seat.passenger.passengerId) == "TERRORIST":
                        button.config(bg="red")
                    elif self.terroristData.get(seat.passenger.passengerId) == "CLEAN":
                        button.config(bg="green")
                    else:
                        button.config(bg="orange")

                if self.highlightPassenger and seat.passenger == self.highlightPassenger:
                    button.config(bg="yellow")

            row += (seatingClass.totalSeats + seatingClass.seatsPerRow - 1) // seatingClass.seatsPerRow + 1

        occupiedSeats = 0
        for i in range(len(classes)):
            seatingClass = classes[i]
            for j in range(len(seatingClass.seats)):
                seat = seatingClass.seats[j]
                if seat.passenger:
                    occupiedSeats += 1

        revenue = 0
        for i in range(len(classes)):
            seatingClass = classes[i]
            for j in range(len(seatingClass.seats)):
                seat = seatingClass.seats[j]
                if seat.passenger:
                    revenue += seat.passenger.luggage * seatingClass.pricePerSeat

        occupiedLabel = tk.Label(self, text=f"Seats occupied: {occupiedSeats}", font=("Arial", 9, "bold"),  bg="gray")
        occupiedLabel.grid(row=row, column=0, columnspan=4, pady=5)

        cargoLabel = tk.Label(self, bg="gray", font=("Arial", 9, "bold"),  text=f"Cargo Filled: {self.plane.currentCargo / self.plane.cargoCapacity * 100:.0f}%")
        cargoLabel.grid(row=row + 1, column=0, columnspan=4, pady=5)

        revenueLabel = tk.Label(self, bg="gray", font=("Arial", 9, "bold") ,text=f"Revenue: Rs. {revenue:,}")
        revenueLabel.grid(row=row + 2, column=0, columnspan=4, pady=5)

management = PIAManagement()
app = SeatReservationSystem(management)
app.mainloop()