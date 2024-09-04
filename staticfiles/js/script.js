function toggleMenu() {

  var menuContainer = document.getElementById("menuContainer");
  var mainContent = document.getElementById("mainContent");

  if (menuContainer.style.left === "0px") {
    menuContainer.style.left = "-250px";
    mainContent.style.marginLeft = "0";
  } else {
    menuContainer.style.left = "0";
    mainContent.style.marginLeft = "250px";
  }
}
  

