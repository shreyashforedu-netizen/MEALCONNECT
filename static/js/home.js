// main.js

document.addEventListener("DOMContentLoaded", () => {
  // 1. Navbar Scroll Effect
  const navbar = document.getElementById("navbar");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

  // 2. Directory Tabs & Live Data Fetching Simulation
  const tabBtns = document.querySelectorAll(".tab-btn");
  const grids = document.querySelectorAll(".entity-grid");
  const spinner = document.getElementById("loading-spinner");
  
  // Mock Data mimicking a live DB response (only public data)
  const mockDatabase = {
    hotels: [
      { name: "Grand Plaza Hotel", location: "Downtown District", type: "Luxury Hotel" },
      { name: "Oceanview Resort", location: "Coastal Bay", type: "Resort" },
      { name: "The Urban Cafe", location: "Tech Park", type: "Restaurant" },
      { name: "Green Leaf Bistro", location: "Westside", type: "Vegan Restaurant" },
      { name: "Skyline Inn", location: "City Center", type: "Boutique Hotel" },
      { name: "Heritage Dining", location: "Old Town", type: "Fine Dining" }
    ],
    ngos: [
      { name: "City Harvest Foundation", location: "Downtown", focus: "Food Rescue" },
      { name: "Nourish The Community", location: "Eastside", focus: "Community Kitchen" },
      { name: "Hope Food Bank", location: "North District", focus: "Food Bank" },
      { name: "Kids Meal Initiative", location: "Southville", focus: "Child Nutrition" }
    ]
  };

  let dataLoaded = false;

  // Function to create an entity card HTML string
  const createCard = (entity, icon) => {
    const metaText = entity.type ? `${entity.type} • ${entity.location}` : `${entity.focus} • ${entity.location}`;
    return `
      <div class="entity-card glass">
        <h3 class="entity-name">${entity.name}</h3>
        <div class="entity-meta">
          <i class="${icon}"></i> ${metaText}
        </div>
      </div>
    `;
  };

  // Function to load and render data
  const loadDirectoryData = async () => {
    // Show spinner, hide grids
    spinner.style.display = "flex";
    grids.forEach(grid => grid.classList.add("hidden"));
    
    try {
      const response = await fetch('/api/public_directory');
      const liveData = await response.json();

      // Render Hotels
      const hotelsContainer = document.getElementById("hotels-list");
      hotelsContainer.innerHTML = liveData.hotels.map(h => createCard(h, "ri-map-pin-line")).join("");

      // Render NGOs
      const ngosContainer = document.getElementById("ngos-list");
      ngosContainer.innerHTML = liveData.ngos.map(n => createCard(n, "ri-map-pin-user-line")).join("");

      dataLoaded = true;
      spinner.style.display = "none";
      
      // Show active tab
      const activeTarget = document.querySelector(".tab-btn.active").dataset.target;
      document.getElementById(activeTarget).classList.remove("hidden");
    } catch (err) {
      spinner.innerHTML = '<p style="color: #e74c3c; text-align: center;">Error loading directory data.</p>';
    }
  };

  // Tab switching logic
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      // Update active button
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      // Update active grid if data is loaded
      if (dataLoaded) {
        grids.forEach(grid => grid.classList.add("hidden"));
        const targetId = btn.dataset.target;
        document.getElementById(targetId).classList.remove("hidden");
      }
    });
  });

  // Intersection Observer to trigger fetch only when the directory section is near
  const directorySection = document.querySelector(".directory-section");
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !dataLoaded) {
        loadDirectoryData();
        observer.unobserve(directorySection);
      }
    });
  }, { threshold: 0.2 });

  observer.observe(directorySection);
});
