window.addEventListener("DOMContentLoaded", (event) => {
  // Toggle the side navigation
  const sidebarToggle = document.body.querySelector("#sidebarToggle");
  if (sidebarToggle) {
    // Uncomment Below to persist sidebar toggle between refreshes
    // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
    //     document.body.classList.toggle('sb-sidenav-toggled');
    // }
    sidebarToggle.addEventListener("click", (event) => {
      event.preventDefault();
      document.body.classList.toggle("sb-sidenav-toggled");
      localStorage.setItem(
        "sb|sidebar-toggle",
        document.body.classList.contains("sb-sidenav-toggled")
      );
    });
  }
});

const flexSwitchCheck = document.body.querySelector("#flexSwitchCheck");
const layoutSidenav_content = document.body.querySelector(
  "#layoutSidenav_content"
);
const sidenav = document.body.querySelector(".sb-sidenav");
const topNav = document.body.querySelector(".sb-topnav");
const mode = document.body.querySelector("#mode");
const text_color = document.body.querySelector(".text_colour");

const toggleMode = () => {
  if (mode.innerHTML === "Light Mode") {
    topNav.classList.remove("navbar-light");
    topNav.classList.remove("bg-light");
    layoutSidenav_content.classList.remove("light_side_content");
    text_color.classList.remove("light");
    sidenav.classList.remove("sb-sidenav-light");

    topNav.classList.add("navbar-dark");
    topNav.classList.add("bg-dark");
    layoutSidenav_content.classList.add("dark_side_content");
    text_color.classList.add("dark");
    sidenav.classList.add("sb-sidenav-dark");

    mode.innerHTML = "Dark Mode";
  } else {
    topNav.classList.add("navbar-light");
    topNav.classList.add("bg-light");
    layoutSidenav_content.classList.add("light_side_content");
    text_color.classList.add("light");
    sidenav.classList.add("sb-sidenav-light");
    
    text_color.classList.remove("dark");
    topNav.classList.remove("navbar-dark");
    topNav.classList.remove("bg-dark");
    layoutSidenav_content.classList.remove("dark_side_content");
    sidenav.classList.remove("sb-sidenav-dark");

    mode.innerHTML = "Light Mode";
  }
};

flexSwitchCheck.addEventListener("click", toggleMode);
