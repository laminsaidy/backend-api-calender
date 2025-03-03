// Temperature conversion program

const textBox = document.getElementById("textBox");
const toFahrenheit = document.getElementById("toFahrenheit");
const toCelsius = document.getElementById("toCelsius");
const result = document.getElementById("result");

function convert() {
  const inputValue = textBox.value.trim(); // Get and trim the input value

  if (inputValue === "") {
    result.textContent = "Please enter a temperature";
    return;
  }

  let temp = Number(inputValue);

  if (toFahrenheit.checked) {
    // Convert Celsius to Fahrenheit
    temp = (temp * 9) / 5 + 32;
    result.textContent = temp.toFixed(1) + "°F";
  } else if (toCelsius.checked) {
    // Convert Fahrenheit to Celsius
    temp = ((temp - 32) * 5) / 9;
    result.textContent = temp.toFixed(1) + "°C";
  } else {
    // No unit selected
    result.textContent = "Please select a unit";
  }
}