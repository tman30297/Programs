// My first Rust program - Hello World with extras!
// Learning Rust syntax: variables, functions, ownership

fn main() {
    // Rust variables are immutable by default - must use 'mut' to change
    let name = "Rust Learner";
    let mut count = 0;
    
    println!("Hello, {}!", name);
    println!("Welcome to Rust programming!");
    println!();
    
    // Demonstrate a simple function call
    let result = add_numbers(5, 3);
    println!("5 + 3 = {}", result);
    
    // Demonstrate string handling (Rust ownership model)
    let s1 = String::from("hello");
    let s2 = s1; // s1 is moved to s2, s1 no longer valid
    
    // This would error: println!("{}", s1); // Error! s1 was moved
    println!("s2 = {}", s2); // This works
    
    // Borrowing instead of moving
    let s3 = String::from("world");
    let len = calculate_length(&s3); // Borrow s3, don't take ownership
    println!("Length of '{}' is {}", s3, len); // s3 still valid!
    
    // Loop example
    println!();
    println!("Counting to 3:");
    while count < 3 {
        count += 1;
        println!("  Count: {}", count);
    }
    
    // For loop (Rust style)
    println!();
    println!("For loop fruits:");
    let fruits = ["apple", "banana", "orange"];
    for fruit in fruits.iter() {
        println!("  - {}", fruit);
    }
    
    println!();
    println!("Program completed successfully! 🦀");
}

// Simple function with return type
fn add_numbers(a: i32, b: i32) -> i32 {
    a + b // No semicolon = return value
}

// Function that borrows a string reference
fn calculate_length(s: &String) -> usize {
    s.len() // Borrowed reference, doesn't take ownership
}
