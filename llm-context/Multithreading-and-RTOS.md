# Multithreaded applications

## Overview

nRF Connect SDK uses the Zephyr RTOS, a real-time OS designed for embedded development. Zephyr includes numerous kernel services and other features including threads, that allow for multithreaded application development. In this lesson, we will go through thread concepts and the thread-related services that are provided by the nRF Connect SDK/Zephyr.

In the exercise section, we will cover how to create threads with different priorities and learn about the scheduler’s behavior through features like time slicing and workqueues.

---

## Bare-metal vs RTOS programming

### Bare-metal application

A bare-metal application, at its core, is just a big loop in the main function right after you have initialized the hardware/software at the device powerup/reset routines. All the execution is sequential logic, in other words, all instructions are executed in sequence unless interrupted by an interrupt service routine (ISR). So the only non-sequential logic you have in bare-metal programming makes use of exceptions.

While bare-metal programming is often associated with greater power efficiency, reduced memory usage, and potentially faster performance, this isn’t always the case. For simple applications, employing a single sequential logic loop can suffice, benefiting from the inherent power efficiency and memory conservation of bare-metal programs. However, as application complexity grows, maintaining firmware architecture solely through sequential logic can become challenging, unscalable, and unportable. This is where the utilization of a real-time operating system (RTOS) proves advantageous.

### RTOS-based application

Designing your application on top of an operating system allows you to have multiple concurrent logics in your application running in different execution units called **threads**, making your architecture simple, as opposed to just one sequential logic running in your main function in standalone mode.

The core of an RTOS is called the **kernel** and controls everything in the system. The other big added advantage is the huge resources of libraries, drivers, and protocol stacks that are natively available by an RTOS like Zephyr.

**Interrupt Service Routines (ISRs)** are available in both RTOS-based applications and bare-metal applications. They are generated asynchronously by the different devices drivers configured (including callback functions) and protocols stacks.

*(Diagram description from original text: Visualization of bare-metal vs RTOS-based application)*

> **Note**: Having the `main()` function is optional in Zephyr RTOS-based applications. This is because the main thread automatically spawned by the RTOS will do the necessary RTOS initialization, including scheduler/kernel setup, and core drivers setup. After that, it will try to call the user-defined `main()`, if one exists. If no `main()` function exists, the main thread will exit. The system will still be functional and other threads can be scheduled normally.

---

## Zephyr RTOS basics

In this unit, we will talk about the execution units within nRF Connect SDK, namely threads, ISRs and we will also talk about the scheduler and its default behavior.

### Threads

A **thread** is the smallest logical unit of execution for the RTOS scheduler (covered later in this topic) that is competing for the CPU time.

In nRF Connect SDK, there are two main types of threads: cooperative threads (negative priority value) and preemptible threads (non-negative priority). Cooperative threads have negative priority and have very limited usage. Therefore, they are not within the scope of this course.

A thread can be in one of the following states at any given time:

*   **Running:** The running thread is the one that is currently being executed by the CPU. This means that the scheduler of the RTOS has already selected this thread as the one that should get the CPU time and loaded this thread’s context into the CPU registers.
*   **Runnable (Ready):** A thread is marked as “Runnable” when it has no other dependencies with other threads or other system resources to proceed further in execution. The only resource this thread is waiting for is the CPU time. The scheduler includes these threads in the scheduling algorithm that selects the next thread to run after the current running thread changes its state.
*   **Non-runnable (Unready):** A thread that has one or more factors that prevent its execution is deemed to be unready, and cannot be selected as the current thread. This can, for example, be because they are waiting for some resource that is not yet available or they have been terminated or suspended. The scheduler does not include these threads in the scheduling algorithm to select the next thread to run.

#### System threads

A **system thread** is a type of thread that is spawned automatically by Zephyr RTOS during initialization. There are always two threads spawned by default, the **main thread** and the **idle thread**.

*   The **main thread** executes the necessary RTOS initializations and calls the application’s `main()` function, if it exists. If no user-defined `main()` is supplied, the main thread will exit normally, though the system would be fully functional.
*   The **idle thread** runs when there is no other work to do, either running an empty loop or, if supported, will activate power management to save power (this is the case for Nordic devices).

#### User-created threads

In addition to system threads, a user can define their own threads to assign tasks to. For example, a user can create a thread to delegate reading sensor data, another thread to process data, and so on. Threads are assigned a priority, which instructs the scheduler how to allocate CPU time to the thread. We will cover creating user-defined threads in-depth in Exercise 1.

#### Workqueue threads

Another common execution unit in nRF Connect SDK is a **work item**, which is nothing more than a user-defined function that gets called by a dedicated thread called a **workqueue thread**.

A workqueue thread is a dedicated thread to process work items that are pulled out of a kernel object called a **workqueue** in a “first in first out” (FIFO) fashion. Each work item has a specified handler function which is called to process the work item. The main use of this is to **offload non-urgent work** from an ISR or a high-priority thread to a lower priority thread.

A system can have multiple workqueue threads; the default one is known as the **system workqueue**, available to any application or kernel code. The thread processing the work items in the system workqueue is a system thread, and you do not need to create and initialize a workqueue if submitting work items to the system workqueue.

*(Diagram description from original text: Workflow of a workqueue)*

As you can see in the image description above, the ISR or high priority thread submits work into a workqueue, and the dedicated workqueue thread pulls out a work item in a FIFO order. The thread that pulls work items from the queue always yields after it has processed one work item, so that other equal priority threads are not blocked for a long time.

The advantage of delegating work as a work item instead of a dedicated thread is that since work items all share one stack (the workqueue stack), a work item is lighter than a thread because no separate stack is allocated for it.

We will cover work items and workqueue threads in-depth in Exercise 3.

### Threads Priority

Threads are assigned an integer value to indicate their priority, which can be either negative or non-negative. **Lower numerical values take precedence over higher values**, meaning a thread with priority 4 will be given higher priority than a thread with priority 7. Similarly, a thread with priority -2 will have higher priority than both a thread with priority 4 and a thread with priority 7.

The scheduler distinguishes between two types of threads based on their priority: **cooperative** and **preemptible**.

*   A thread with a **negative priority** is classified as a **cooperative thread**. Once a cooperative thread becomes the current thread, it will remain so until it performs an action that makes it unready (e.g., yields, sleeps, waits for an event).
*   A thread with a **non-negative priority** is classified as a **preemptible thread**. Once a preemptible thread becomes the current thread, it may be replaced (preempted) at any time if a cooperative thread or a preemptible thread of higher or equal priority becomes ready.

The number of non-negative priorities (for preemptible threads) is configurable through the Kconfig symbol `CONFIG_NUM_PREEMPT_PRIORITIES` and is, by default, equal to 15. The main thread has a priority of 0, while the idle thread has a priority of 15 by default.

Similarly, the number of negative priorities (for cooperative threads) is configurable through the Kconfig symbol `CONFIG_NUM_COOP_PRIORITIES` and is, by default, equal to 16. (Cooperative threads are not covered in this fundamentals course).

### Scheduler

Like anything in the physical world, CPU time is a limited resource, and when an application has multiple concurrent logics, it’s not guaranteed that there would be enough CPU time for all of them to run concurrently. This is where the **scheduler** comes in. The scheduler is the part of the RTOS responsible for scheduling which tasks are running (i.e., using CPU time) at any given time. It does this using a scheduling algorithm to determine which task should be the next to run.

> **Note**: The number of running threads possible at any instant is equal to the number of application cores. For example on the nRF52840, there is one application core, allowing for only one thread to be running at a time.

#### Rescheduling point

Zephyr RTOS is by default a **tickless RTOS**, meaning it is completely event-driven. Instead of having periodic timer interrupts to wake up the scheduler, it is woken based on events known as **rescheduling points**.

A rescheduling point is an instant in time when the scheduler gets called to select the thread to run next. Any time the state of the Ready threads changes, a rescheduling point is triggered. Some examples of rescheduling points are:

*   When a thread calls `k_yield()`, the thread’s state is changed from “Running” to “Ready”.
*   Unblocking a thread by giving/sending a kernel synchronization object (like a semaphore, mutex, or alert) causes the thread’s state to be changed from “Unready” to “Ready”.
*   When a receiving thread gets new data from other threads using data passing kernel objects, the data receiving thread’s state is changed from “Waiting” to “Ready”.
*   When time slicing is enabled (covered in Exercise 2) and the thread has run continuously for the maximum time slice time allowed, the thread’s state is changed from “Running” to “Ready”.

### ISRs

Interrupt Service Routines (ISRs) are generated asynchronously by device drivers and protocol stacks. **They are not scheduled.** This includes callback functions, which are the application extension of ISRs. It is important to remember that ISRs **preempt** the execution of the current thread, allowing the response to occur with very low overhead. Thread execution resumes only once all ISR work has been completed.

Therefore, it is crucial to ensure that ISRs (including callback functions) **do not contain time-consuming work or involve blocking functionalities**, as they will starve all other threads. Work that is time-consuming or involves blocking should be handed off to a thread using work items or other appropriate mechanisms, as we will see in Exercise 3.

---

## Exercise 1: Thread creation and priorities

In this exercise, we will learn how to create and initialize two threads and learn how they can affect one another with their priorities. There are two ways to create a thread in Zephyr: dynamically (at run-time) through `k_thread_create()` and statically (at compile time) using the `K_THREAD_DEFINE()` macro. The static method is more frequently used.

`K_THREAD_DEFINE()` API signature:
*(Description of image: K_THREAD_DEFINE API arguments)*

### Exercise steps

1.  In the GitHub repository for this course, open the base code for this exercise, found in `l7/l7_e1` (select your version subfolder). Open it as an existing application in VS Code.

#### Creating and initializing threads

2.  Define the stack size and scheduling priority for two threads near the top of `src/main.c`:
    ```c
    #define STACKSIZE 1024
    #define THREAD0_PRIORITY 7
    #define THREAD1_PRIORITY 7
    ```
    Even though the threads are simple, we use a stack size of 1024 bytes. Stack sizes should typically be powers of two.
    > **Note**: In real applications, choose stack sizes carefully to avoid unnecessary memory usage.
    We give both threads the same priority initially.

3.  The thread entry functions (`thread0` and `thread1`) are provided but empty. Make them print a simple string in a loop. Add inside each function's `while(1)` loop (adjust the string for `thread1`):
    ```c
    // Inside thread0():
    printk("Hello, I am thread0\n");

    // Inside thread1():
    printk("Hello, I am thread1\n");
    ```
    Since the threads have no dependencies and neither yield nor sleep yet, they will always be in the “Runnable” state, competing for the CPU.

4.  Define the two threads using `K_THREAD_DEFINE()`. Add these lines after the thread entry function definitions:
    ```c
    K_THREAD_DEFINE(thread0_id, STACKSIZE, thread0, NULL, NULL, NULL,
            THREAD0_PRIORITY, 0, 0);
    K_THREAD_DEFINE(thread1_id, STACKSIZE, thread1, NULL, NULL, NULL,
            THREAD1_PRIORITY, 0, 0);
    ```
    *   `thread0_id`, `thread1_id`: Names (thread IDs) for the threads.
    *   `STACKSIZE`: Stack size defined earlier.
    *   `thread0`, `thread1`: Thread entry functions.
    *   `NULL, NULL, NULL`: Optional arguments passed to the entry functions (none here).
    *   `THREAD0_PRIORITY`, `THREAD1_PRIORITY`: Priorities defined earlier.
    *   `0`: Optional thread options (0 means default, no special options like `K_ESSENTIAL`).
    *   `0`: Optional scheduling delay (0 means start immediately in ready state).

5.  Build the application and flash it. Observe the serial terminal output:
    ```terminal
    *** Booting nRF Connect SDK ***
    Hello, I am thread0
    Hello, I am thread0
    Hello, I am thread0
    ... (only thread0 prints)
    ```
    Notice only `thread0` runs. Because `thread0` never yields or sleeps (never enters a state that triggers a rescheduling point where it might lose the CPU), it starves `thread1`.

#### Thread yielding

To avoid starvation, we can make `thread0` voluntarily yield using `k_yield()`.

`k_yield()` causes the current thread to relinquish the CPU to another thread of the *same or higher* priority. The yielding thread remains “Runnable” but is moved to the end of the ready queue for its priority level. If no other threads of the same or higher priority are ready, the yielding thread runs again immediately.

> **Note**: To allow *lower* priority threads to run, the current thread must enter a “Non-runnable” state (e.g., using `k_sleep()`).

Let's make `thread0` yield after printing.

6.  Add `k_yield();` inside the `while(1)` loop in `thread0`, after the `printk()` call:
    ```c
    void thread0(void)
    {
        while (1) {
            printk("Hello, I am thread0\n");
            k_yield(); // Add this line
        }
    }
    ```
7.  Build and flash. Observe the output:
    ```terminal
    *** Booting nRF Connect SDK ***
    Hello, I am thread0
    Hello, I am thread1
    Hello, I am thread1
    Hello, I am thread1
    ... (only thread1 prints after the first message from thread0)
    ```
    `thread0` prints once and yields. The scheduler sees `thread1` (same priority, ready) and switches to it. Since `thread1` never yields, it runs forever, now starving `thread0`.

8.  Make `thread1` yield as well. Add `k_yield();` inside the `while(1)` loop in `thread1`, after its `printk()` call:
    ```c
    void thread1(void)
    {
        while (1) {
            printk("Hello, I am thread1\n");
            k_yield(); // Add this line
        }
    }
    ```
9.  Build and flash. Observe the output:
    ```terminal
    *** Booting nRF Connect SDK ***
    Hello, I am thread0
    Hello, I am thread1
    Hello, I am thread0
    Hello, I am thread1
    Hello, I am thread0
    Hello, I am thread1
    ... (threads alternate)
    ```
    *(Diagram description from original text: Timeline showing threads alternating execution due to yielding)*

    Now, each thread yields after printing. The scheduler finds the other (equal priority, ready) thread and switches, resulting in alternation. However, frequent yielding invokes the scheduler often, consuming CPU time and power. Better architecture involves designing threads with appropriate priorities and considerate blocking (sleeping/waiting).

#### Thread sleeping

Since printing is non-critical here, sleeping is more efficient than yielding constantly. `k_sleep()` (or derivatives like `k_msleep()`) puts a thread into the “Non-runnable” state for a duration.

> **More on this**: `k_sleep()` takes a `k_timeout_t` (construct with `K_MSEC()`, `K_SECONDS()`, etc.). Simpler derivatives like `k_msleep()` and `k_usleep()` take integer time units directly.

10. Replace `k_yield()` in both threads with `k_msleep(5);` (sleep for 5 milliseconds):
    ```c
    void thread0(void)
    {
        while (1) {
            printk("Hello, I am thread0\n");
            k_msleep(5); // Replaced k_yield()
        }
    }

    void thread1(void)
    {
        while (1) {
            printk("Hello, I am thread1\n");
            k_msleep(5); // Replaced k_yield()
        }
    }
    ```
11. Build and flash. The output looks the same as step 9 (alternating prints), but the underlying behavior is different:
    ```terminal
    *** Booting nRF Connect SDK ***
    Hello, I am thread0
    Hello, I am thread1
    Hello, I am thread0
    Hello, I am thread1
    ... (threads alternate)
    ```
    *(Diagram description from original text: Timeline showing threads sleeping, allowing idle thread to run)*

    When both threads sleep and no other threads are ready, the scheduler runs the **idle thread**, allowing the system to enter low-power states between thread executions.

**Conclusion:**

*   `k_yield()`: Changes state from Running -> Runnable. Thread remains eligible to run immediately if no equal/higher priority threads are ready. Good for cooperative sharing among equal priorities.
*   `k_sleep()`: Changes state from Running -> Non-runnable (for duration) -> Runnable. Thread is ineligible to run during sleep. Better for introducing delays and allowing lower-priority or idle thread execution.

The solution for this exercise can be found in the GitHub repository, `l7/l7_e1_sol` (select your version subfolder).

---

## Exercise 2: Time slicing

If you don’t want to manually manage yielding between equal priority threads, you can enable **time slicing**. The scheduler will automatically preempt a running thread after a configured time slice, allowing other threads of the *same priority* to run.

In this exercise, we will observe how time slicing affects thread interaction.

### Exercise steps

1.  In the GitHub repository, open the base code for this exercise: `l7/l7_e2` (select your version subfolder).
2.  Observe `main.c`. The threads neither sleep nor yield but use `k_busy_wait()`:
    ```c
    void thread0(void)
    {
        while (1) {
                printk("Hello, I am thread0\n");
                k_busy_wait(1000000); // Busy wait for 1 second
        }
    }

    void thread1(void)
    {
        while (1) {
                printk("Hello, I am thread1\n");
                k_busy_wait(1000000); // Busy wait for 1 second
        }
    }
    ```
    Without time slicing, the first thread to run would block the other indefinitely. `k_busy_wait()` executes a do-nothing loop for a specified time (microseconds), keeping the CPU busy. **It is intended for debugging only, not production code.**

3.  Enable time slicing in `prj.conf`:
    ```kconfig
    # STEP 3: Enable Time Slicing
    CONFIG_TIMESLICING=y
    CONFIG_TIMESLICE_SIZE=10 # milliseconds
    CONFIG_TIMESLICE_PRIORITY=0 # Max priority level affected by time slicing
    ```
    *   `CONFIG_TIMESLICING=y`: Enables the feature.
    *   `CONFIG_TIMESLICE_SIZE=10`: Sets the maximum time slice to 10 ms.
    *   `CONFIG_TIMESLICE_PRIORITY=0`: Sets the *highest* priority level where time slicing applies. Threads with priority 0 or numerically higher (lower logical priority, e.g., 1, 2,... 7) will be time-sliced if multiple threads exist at that level. Threads with priority numerically lower than 0 (e.g., -1, -2) or higher logical priority are not time-sliced. Setting it to 0 ensures our priority 7 threads (from Exercise 1, default here is likely similar) are affected. **Remember: Time slicing only affects threads of the *same* priority.**

4.  Build and flash the application. Observe the output:
    ```terminal
    *** Booting nRF Connect SDK ***
    Hello, I am thread0
    Hello, I am thread1
    Hello, I am thread0
    Hello, I am thread1
    ... (output alternates, possibly with interrupted printk messages)
    Hello, I amHello, I am  thread0
    thread1
    ```
    The scheduler preempts the running thread after ~10 ms, even mid-`printk()`. The other thread resumes. Because `printk` itself isn't atomic with respect to time slicing preemption, you might see interleaved output.

    *(Diagram description from original text: Timeline showing preemptive time slicing)*

    The scheduler forces context switches between the equal-priority threads every 10 ms.

5.  Now, let's see what happens with different priorities. Change `THREAD0_PRIORITY` to 6 in `main.c`, making it higher priority than `thread1` (priority 7):
    ```c
    #define THREAD0_PRIORITY 6
    #define THREAD1_PRIORITY 7
    ```
6.  Build and flash. Observe the output:
    ```terminal
    *** Booting nRF Connect SDK ***
    Hello, I am thread0
    Hello, I am thread0
    Hello, I am thread0
    ... (only thread0 prints)
    ```
    `thread0` runs uninterrupted, starving `thread1`. Even though time slicing is enabled and configured to potentially affect priority 6, the scheduler preempts `thread0` every 10 ms *only to check for other ready threads of priority 6 or higher*. Since `thread1` has lower priority (7), `thread0` immediately gets the CPU back and runs forever. **Time slicing does not grant CPU time to lower-priority threads.**

The solution for this exercise can be found in the GitHub repository, `l7/l7_e2_sol` (select your version subfolder).

---

## Exercise 3: Workqueue creation and work item submission

Since higher priority threads can starve lower priority ones, it's good practice to **offload non-urgent work** from high-priority threads to lower-priority execution contexts, such as workqueues.

In this exercise, we will create a workqueue and submit work items to it from a higher-priority thread.

### Exercise steps

1.  In the GitHub repository, open the base code for this exercise: `l7/l7_e3` (select your version subfolder).

#### Threads with different priorities

2.  Define priorities for three threads near the top of `main.c`. `thread0` will be high priority, `thread1` medium, and the workqueue thread low priority:
    ```c
    #define THREAD0_PRIORITY 2
    #define THREAD1_PRIORITY 3
    #define WORKQ_PRIORITY   4
    ```
3.  Examine `thread0` (provided in the base code). It measures and prints the duration of `emulate_work()` and sleeps for 20 ms in a loop:
    ```c
    void thread0(void)
    {
        uint64_t time_stamp;
        int64_t delta_time;

        while (1) {
            time_stamp = k_uptime_get();
            emulate_work(); // Simulate work directly in the high-priority thread
            delta_time = k_uptime_delta(&time_stamp);

            printk("thread0 yielding this round in %lld ms\n", delta_time);
            k_msleep(20);
        }
    }
    ```
4.  Make `thread1` do the same thing. Add the following code for `thread1`:
    ```c
    void thread1(void)
    {
        uint64_t time_stamp;
        int64_t delta_time;

        while (1) {
            time_stamp = k_uptime_get();
            emulate_work(); // Simulate work directly in the medium-priority thread
            delta_time = k_uptime_delta(&time_stamp);

            printk("thread1 yielding this round in %lld ms\n", delta_time);
            k_msleep(20);
        }
    }
    ```
    `thread1` will be frequently preempted by the higher-priority `thread0`.

5.  Define an inline function `emulate_work()` before the thread functions:
    ```c
    static inline void emulate_work(void) // Added void for clarity
    {
        // Loop to consume CPU time
        for(volatile int count_out = 0; count_out < 300000; count_out ++);
    }
    ```
    This function takes roughly ~24 ms on an nRF54L15 @ 128 MHz (~50 ms on nRF52840 @ 64 MHz).

6.  Build and flash. Observe the output (times may vary based on SoC/clock speed):
    ```terminal
    *** Booting nRF Connect SDK ... ***
    *** Using Zephyr OS ... ***
    thread0 yielding this round in 23 ms
    thread0 yielding this round in 24 ms
    thread1 yielding this round in 50 ms // Takes much longer due to preemption
    thread0 yielding this round in 23 ms
    thread0 yielding this round in 23 ms
    thread1 yielding this round in 50 ms
    ...
    ```
    `thread0` (higher priority) completes its work quickly. `thread1` takes significantly longer because `thread0` preempts it frequently while `thread0` runs `emulate_work()`.

    *(Diagram description from original text: Timeline showing thread1 being preempted by thread0)*

#### Offloading work from high priority task

Since `emulate_work()` represents non-urgent processing for `thread0`, let's offload it to a lower-priority workqueue thread to avoid blocking `thread1` unnecessarily.

7.  Define a structure to hold work item information and the work handler function *before* `main()`:
    ```c
    // Structure to pass work item info (can be extended)
    struct work_info {
        struct k_work work; // Kernel work item structure MUST be first member
        char name[25];      // Example: data associated with the work
    } my_work; // Global instance of our work item

    // Work handler function - executes the offloaded work
    void offload_function(struct k_work *work_item)
    {
        // struct work_info *work_data = CONTAINER_OF(work_item, struct work_info, work); // Get container struct if needed
        // printk("Executing work: %s\n", work_data->name); // Example using associated data
        emulate_work(); // Perform the actual work
    }
    ```
8.  In `main()`, before defining threads, define the workqueue stack and initialize the workqueue and work item. Add these lines (assuming `STACKSIZE` is defined):
    ```c
    // Define stack area for the workqueue's thread
    K_THREAD_STACK_DEFINE(my_stack_area, STACKSIZE);
    // Define the workqueue itself
    struct k_work_q offload_work_q;

    // Inside main(), initialize the workqueue
    k_work_queue_init(&offload_work_q);

    // Start the workqueue thread
    k_work_queue_start(&offload_work_q, my_stack_area,
                       K_THREAD_STACK_SIZEOF(my_stack_area), WORKQ_PRIORITY,
                       NULL); // No specific options

    // Initialize the work item, linking it to the handler function
    strcpy(my_work.name, "Thread0 emulate_work()"); // Example: set associated data
    k_work_init(&my_work.work, offload_function);
    ```
9.  Modify `thread0` to submit the work item instead of calling `emulate_work()` directly. Replace the `emulate_work();` line inside `thread0`'s `while` loop with:
    ```c
    // Inside thread0's while loop:
    // time_stamp = k_uptime_get(); // Keep timing if desired
    // emulate_work(); // REMOVE THIS LINE
    k_work_submit_to_queue(&offload_work_q, &my_work.work); // Submit work item
    // delta_time = k_uptime_delta(&time_stamp); // Timing now measures submission overhead
    ```
    `thread0` now quickly submits the work and goes back to sleep, allowing `thread1` more CPU time. The actual `emulate_work()` runs later in the lower-priority workqueue thread.

10. Build and flash. Observe the output:
    ```terminal
    *** Booting nRF Connect SDK ... ***
    *** Using Zephyr OS ... ***
    thread0 yielding this round in 0 ms // Very fast, just submits work
    thread0 yielding this round in 0 ms
    thread1 yielding this round in 26 ms // Much faster now!
    thread0 yielding this round in 0 ms
    thread0 yielding this round in 0 ms
    thread1 yielding this round in 26 ms
    ...
    ```
    *(Timings relative to nRF54L15 DK @ 128 MHz example in original text)*

    *(Diagram description from original text: Timeline showing thread0 quickly submitting work, thread1 running more, and workqueue thread executing later)*

    `thread0` now completes its loop very quickly (<1 ms) because it only submits the work item. This gives `thread1` significantly more time to execute `emulate_work()` without being preempted as often by `thread0`. The actual `emulate_work()` initiated by `thread0` runs in the `offload_work_q` thread at `WORKQ_PRIORITY` (lower priority) when both `thread0` and `thread1` are sleeping. This demonstrates better resource sharing by offloading non-critical work.

The solution for this exercise can be found in the GitHub repository, `l7/l7_e3_sol` (select your version subfolder).# Thread synchronization

## Overview

In multithreaded applications, the need for thread synchronization arises when multiple threads are running concurrently. In this lesson, we will explain the need for thread synchronization and how to use semaphores and mutexes as thread synchronization mechanisms.

In the exercise section, we will highlight two common thread synchronization problems and show how to solve them using semaphores and mutexes.

### Thread synchronization

In a multithreaded application, there are multiple threads running concurrently. If more than one thread tries to access the same piece of code simultaneously, usually referred to as the **critical section**, this can lead to unexpected or erroneous behavior. This is where the need for **thread synchronization** arises; it’s a mechanism to ensure that only one thread executes the critical section at any given time.

Two mechanisms you can utilize to achieve thread synchronization are **semaphores** or **mutexes**. They have some differing properties, but in essence they are both variables that are changed before and after the critical section by a thread to make sure that no other threads can execute the segment before that thread has completed it. The main differences are that semaphores have a maximum count value that is set at initialization, while mutexes have an ownership property (i.e., only the thread that locks it can unlock it).

In the following sections, we will discuss in more detail about both semaphores and mutexes, including a list of properties and a visualization description. There are also two exercises to be completed, practicing how to use semaphores and mutexes as thread synchronization mechanisms.

### Semaphores

In its simplest form, a **semaphore** is merely a plain variable that is changed, indicating the status of the common resource. Semaphores can be seen as a resource-sharing mechanism, where you have a finite instance of a resource that you want to manage access for multiple threads. They are more of a signaling mechanism used to control access to a given number of instances of a resource.

Semaphores have the following properties:

*   At initialization, you set an initial count (greater or equal to 0) and a maximum limit.
*   **“Give”** (`k_sem_give()`): Increments the semaphore count unless the count is already at the maximum limit. “Give” can be done from any thread or ISR.
*   **“Take”** (`k_sem_take()`): Decrements the semaphore count unless the semaphore is unavailable (count at zero). Any thread trying to take an unavailable semaphore needs to wait (block) until another thread makes it available (by giving the semaphore). “Take” can usually only block within threads, not ISRs (ISRs can take with `K_NO_WAIT` but cannot block).
*   **No ownership:** A semaphore can be taken by one thread and given by any other thread or ISR.
*   **No priority inheritance:** The thread taking the semaphore is not eligible for priority inheritance because any thread can give the semaphore.

*(Diagram description from original text: Semaphore properties visualization)*

> **Note**:
> *   You may initialize a “full” semaphore (count equal to limit) to limit the number of threads able to execute the critical section concurrently.
> *   You may also initialize an “empty semaphore” (count equal to 0, limit equal to 1) to create a gate where no waiting thread may pass until the semaphore is given first.

### Mutexes

As opposed to semaphores, **mutexes** (Mutual Exclusion locks) can generally only take two logical states: **locked** or **unlocked**. Additionally, mutexes have **ownership properties**: only the thread that locks (acquires) the mutex can unlock (release) it. Think of it as a locking/unlocking mechanism with a single key for a single resource (like a critical section or shared data structure).

A thread wishing to access the protected resource must first acquire the unlocked mutex. If the mutex is already locked by another thread, the requesting thread blocks until the owner unlocks it.

A typical use of a mutex is to protect a critical section of code accessed by multiple threads, preventing race conditions where shared data could be corrupted if accessed concurrently.

Mutexes have the following properties:

*   **Locking** (`k_mutex_lock()`): A thread acquires the mutex if unlocked. If already locked by another thread, the requesting thread blocks. Recursive locking (the owner locking again) is allowed and increments an internal lock count.
*   **Unlocking** (`k_mutex_unlock()`): Decrements the internal lock count. When the count reaches zero, the mutex becomes unlocked and available for other threads to acquire.
*   **Ownership:** Only the thread that locked the mutex can unlock it.
*   **Context:** Mutex locking and unlocking can only be done from threads, **not** ISRs (due to ownership and potential blocking).
*   **Priority Inheritance:** The thread locking the mutex *is* eligible for priority inheritance. If a higher-priority thread blocks waiting for the mutex, the scheduler may temporarily boost the priority of the mutex-holding thread to help it finish faster and release the mutex, preventing priority inversion.

*(Diagram description from original text: Mutex properties visualization)*

---

## Exercise 1: Semaphores

Let’s see the use of semaphores in action. In this exercise, we will initialize a semaphore that will track the availability of 10 instances of a hypothetical shared resource. There will be one **consumer thread** trying to acquire the resource and one **producer thread** releasing it.

### Exercise steps

1.  In the GitHub repository for this course, open the base code for this exercise, found in `l8/l8_e1` (select your version subfolder). Open it as an existing application in VS Code.
2.  Set the thread priorities in `src/main.c`. Make the consumer higher priority to demonstrate contention:
    ```c
    #define PRODUCER_PRIORITY        5
    #define CONSUMER_PRIORITY        4
    ```
3.  Define a variable to track the available resource instances (initially 10):
    ```c
    volatile uint32_t available_instance_count = 10;
    ```
4.  Create the producer thread function. It releases the resource (increments count) and sleeps randomly:
    ```c
    void producer(void)
    {
        printk("Producer thread started\n");
        while (1) {
            release_access(); // Function defined later
            // Assume the resource instance access is released at this point
            k_msleep(500 + sys_rand32_get() % 10); // Sleep 500-509 ms
        }
    }
    ```
5.  Create the consumer thread function. It gets the resource (decrements count) and sleeps randomly:
    ```c
    void consumer(void)
    {
        printk("Consumer thread started\n");
        while (1) {
            get_access(); // Function defined later
            // Assume the resource instance is acquired and being used here
            k_msleep(sys_rand32_get() % 10); // Sleep 0-9 ms
        }
    }
    ```
6.  Define the `get_access()` and `release_access()` functions (before the thread functions):
    6.1 In `get_access()`, decrement the count and print:
    ```c
    void get_access(void)
    {
        available_instance_count--;
        printk("Resource taken and available_instance_count = %d\n", available_instance_count);
    }
    ```
    6.2 In `release_access()`, increment the count and print:
    ```c
    void release_access(void)
    {
        available_instance_count++;
        printk("Resource given and available_instance_count = %d\n", available_instance_count);
    }
    ```
    Currently, there are no checks. If `available_instance_count` goes below 0 or above 10, it indicates a race condition.

7.  Define the threads using `K_THREAD_DEFINE` after the function definitions:
    ```c
    K_THREAD_DEFINE(producer_id, 1024, producer, NULL, NULL, NULL,
                    PRODUCER_PRIORITY, 0, 0);
    K_THREAD_DEFINE(consumer_id, 1024, consumer, NULL, NULL, NULL,
                    CONSUMER_PRIORITY, 0, 0);
    ```
8.  Build and flash. Observe the terminal output. You will likely see negative counts, indicating the race condition:
    ```terminal
    *** Booting nRF Connect SDK ... ***
    Consumer thread started
    Resource taken and available_instance_count = 9
    Producer thread started
    Resource taken and available_instance_count = 8
    Resource taken and available_instance_count = 7
    ...
    Resource taken and available_instance_count = 0
    Resource taken and available_instance_count = -1 // ERROR!
    Resource taken and available_instance_count = -2 // ERROR!
    ... (counts become increasingly negative)
    Resource given and available_instance_count = -67 // Producer eventually adds back
    ...
    ```
    The higher-priority consumer runs more often, decrementing the count below zero because there's no mechanism preventing it from taking a non-existent resource.

9.  **Fix the race condition using a semaphore.** Define a semaphore near the top of the file (after includes, before variable definitions) with an initial count of 10 (matching available resources) and a limit of 10:
    ```c
    // STEP 9: Define semaphore
    K_SEM_DEFINE(instance_monitor_sem, 10, 10); // initial_count=10, count_limit=10
    ```
10. Modify the access functions to use the semaphore:
    10.1 In `get_access()`, **take** the semaphore *before* decrementing the count. `K_FOREVER` means wait indefinitely if unavailable:
    ```c
    void get_access(void)
    {
        // STEP 10.1: Take semaphore
        k_sem_take(&instance_monitor_sem, K_FOREVER);
        available_instance_count--;
        printk("Resource taken and available_instance_count = %d\n", available_instance_count);
    }
    ```
    10.2 In `release_access()`, **give** the semaphore *after* incrementing the count:
    ```c
    void release_access(void)
    {
        available_instance_count++;
        printk("Resource given and available_instance_count = %d\n", available_instance_count);
        // STEP 10.2: Give semaphore
        k_sem_give(&instance_monitor_sem);
    }
    ```
    Now, the consumer thread will block on `k_sem_take` if the semaphore count (representing available resources) is 0, waiting until the producer calls `k_sem_give`.

11. Build and flash again. Observe the output:
    ```terminal
    *** Booting nRF Connect SDK ... ***
    Consumer thread started
    Resource taken and available_instance_count = 9
    Producer thread started
    Resource taken and available_instance_count = 8
    ...
    Resource taken and available_instance_count = 1
    Resource taken and available_instance_count = 0
    // Consumer now blocks here, waiting for producer
    Resource given and available_instance_count = 1 // Producer runs, gives semaphore
    Resource taken and available_instance_count = 0 // Consumer runs, takes semaphore
    Resource given and available_instance_count = 1
    Resource taken and available_instance_count = 0
    ... (count stays between 0 and 10)
    ```
    The `available_instance_count` now correctly stays between 0 and 10. The semaphore successfully synchronizes access to the limited resource.

The solution for this exercise can be found in the GitHub repository, `l8/l8_e1_sol` (select your version subfolder).

---

## Exercise 2: Mutexes

In this exercise, we will create an application with two threads accessing the same section of code that modifies shared variables. We'll observe a race condition when both threads run concurrently and then use a mutex to protect the critical section and ensure correct behavior.

The threads will have the same priority, and time slicing will be enabled (10 ms) so they preempt each other, increasing the likelihood of the race condition occurring.

### Exercise steps

1.  In the GitHub repository, open the base code for this exercise: `l8/l8_e2` (select your version subfolder).
2.  Enable multithreading in `prj.conf` (though often enabled by default):
    ```kconfig
    CONFIG_MULTITHREADING=y
    # Enable time slicing for demonstration
    CONFIG_TIMESLICING=y
    CONFIG_TIMESLICE_SIZE=10
    CONFIG_TIMESLICE_PRIORITY=0
    ```
3.  Set equal priorities for the threads in `src/main.c`:
    ```c
    #define THREAD0_PRIORITY        4
    #define THREAD1_PRIORITY        4
    ```
4.  Define the thread entry functions. Both call `shared_code_section()`. Comment out the call in `thread1` initially:
    ```c
    void thread0(void)
    {
        printk("Thread 0 started\n");
        while (1) {
            shared_code_section();
        }
    }

    void thread1(void)
    {
        printk("Thread 1 started\n");
        while (1) {
            // shared_code_section(); // Initially commented out
        }
    }
    ```
5.  Define two global counters and their expected combined total:
    ```c
    #define COMBINED_TOTAL   40
    int32_t increment_count = 0;
    int32_t decrement_count = COMBINED_TOTAL;
    ```
6.  Define the `shared_code_section()` function (before the thread functions). This function modifies both counters:
    ```c
    void shared_code_section(void)
    {
        increment_count += 1;
        increment_count = increment_count % COMBINED_TOTAL; // Wrap increment counter
        decrement_count -= 1;
        if (decrement_count == 0) {
            decrement_count = COMBINED_TOTAL; // Wrap decrement counter
        }
        // Check invariant AFTER modifications
        check_counters(); // Separate check function called later
    }
    ```
    > **Note**: If implemented correctly without interruption, `increment_count + decrement_count` should *always* equal `COMBINED_TOTAL`. A race condition occurs if a thread switch happens *between* the modification of `increment_count` and `decrement_count`.

7.  Define a `check_counters()` function (called by `shared_code_section`) to print an error if the invariant is broken:
    ```c
    void check_counters(void) // Renamed for clarity
    {
        if (increment_count + decrement_count != COMBINED_TOTAL) {
            printk("Race condition happened!\n");
            printk("Increment_count (%d) + Decrement_count (%d) = %d \n",
                    increment_count, decrement_count, (increment_count + decrement_count));
            // Sleep briefly to avoid flooding console if error persists
            k_msleep(400 + sys_rand32_get() % 10);
        }
    }
    ```
    *(Ensure `shared_code_section` calls `check_counters()` at the end)*
8.  Define the threads using `K_THREAD_DEFINE` (add scheduling delay for terminal connection):
    ```c
    K_THREAD_DEFINE(thread0_id, 1024, thread0, NULL, NULL, NULL,
                    THREAD0_PRIORITY, 0, 5000); // 5 sec delay
    K_THREAD_DEFINE(thread1_id, 1024, thread1, NULL, NULL, NULL,
                    THREAD1_PRIORITY, 0, 5000); // 5 sec delay
    ```
    > **Note**: The 5000 ms startup delay gives time to connect the serial terminal before threads start running.

9.  Build and flash. Observe the output. With only `thread0` calling `shared_code_section()`, no "Race condition" messages should appear:
    ```terminal
    *** Booting nRF Connect SDK ... ***
    Thread 0 started
    Thread 1 started
    (No further output, indicating invariant holds)
    ```
10. **Introduce the race condition.** Uncomment the `shared_code_section();` line in `thread1`:
    ```c
    void thread1(void)
    {
        printk("Thread 1 started\n");
        while (1) {
            shared_code_section(); // Uncomment this line
        }
    }
    ```
11. Build and flash again. Observe the output. You should now see "Race condition" messages frequently:
    ```terminal
    *** Booting nRF Connect SDK ... ***
    Thread 0 started
    Thread 1 started
    Race condition happened!
    Increment_count (6) + Decrement_count (35) = 41
    Race condition happened!
    Increment_count (7) + Decrement_count (34) = 41
    Race condition happened!
    Increment_count (0) + Decrement_count (1) = 1
    ... (various incorrect sums)
    ```
    This happens because time slicing preempts one thread *after* it modifies `increment_count` but *before* it modifies `decrement_count`. The other thread then runs, modifies the counters based on the inconsistent intermediate state, leading to the invariant `sum == COMBINED_TOTAL` being broken when checked.

12. **Fix the race condition using a mutex.**
    12.1 Define a mutex globally (near the top of the file):
    ```c
    // STEP 11: Define mutex
    K_MUTEX_DEFINE(test_mutex);
    ```
    12.2 Modify `shared_code_section()` to lock the mutex *before* accessing the shared counters and unlock it *after* modifications are complete (but *before* the check, or move the check inside):
    ```c
    void shared_code_section(void)
    {
        // STEP 12.1: Lock mutex
        k_mutex_lock(&test_mutex, K_FOREVER);

        // --- Critical Section Start ---
        increment_count += 1;
        increment_count = increment_count % COMBINED_TOTAL;
        decrement_count -= 1;
        if (decrement_count == 0) {
            decrement_count = COMBINED_TOTAL;
        }
        // --- Critical Section End ---

        // STEP 12.2: Unlock mutex
        k_mutex_unlock(&test_mutex);

        // Check can be outside the lock now, as modifications were atomic relative to other threads
        check_counters();
    }
    ```
    Now, only one thread can execute the code between `k_mutex_lock` and `k_mutex_unlock` at a time, ensuring the counter modifications happen atomically with respect to other threads accessing the same critical section.

13. Build and flash. Observe the output. No "Race condition" messages should appear, similar to the output in step 9:
    ```terminal
    *** Booting nRF Connect SDK ... ***
    Thread 0 started
    Thread 1 started
    (No further output)
    ```
    The mutex successfully protects the critical section, ensuring the integrity of the shared variables.

The solution for this exercise can be found in the GitHub repository, `l8/l8_e2_sol` (select your version subfolder).# Zephyr RTOS: Beyond the basics

## Overview

In this lesson, we will dive into thread management and data passing in the nRF Connect SDK/Zephyr. We have two execution contexts: **Thread context** and **Interrupt context**. Each context has its own usage and timing implications.

We will first examine the different execution primitives, and how different types of threads and different types of interrupts co-exist. Then we will take a closer look at the life cycle of a thread and how the scheduler works. After that, we will also cover frequently used data-passing techniques such as message queues and FIFOs

At the end of the lesson, you will have a solid understanding of the options available to schedule application tasks and their different time constraints. You will also gain a good hands-on grasp on how to safely pass data between threads and the kernel options available.

---

## Boot-up sequence & execution context

For implementing tasks for your application code, you need to pick the proper execution primitive (pre-emptible thread, cooperative thread, work queue, etc.) and set its priority correctly to not block other tasks that are running on the CPU while you also meet the time requirements of the task.

One of the main goals of this lesson is to learn how to schedule application tasks using the right execution primitive with the right priority level. But before we can dive into the topic of choosing the right execution method to run a given task, we need to consider the following questions:

*   How does an nRF Connect SDK application boot up?
*   What are the out-of-the-box threads and ISR in an application, and what is their priority and execution nature?
*   What is the difference between interrupt and thread contexts, and what to do in each?

### Boot-up sequence

1.  **Early Boot Sequence (C Code Preparation phase)**
    The primary function of the early boot sequence is to transition the system from its reset state to a state where it becomes capable of executing C code, thereby initiating the kernel initialization sequence. This stage is a pretty standard phase in embedded devices; as an application developer, it is not of much interest.

2.  **Kernel Initialization**
    This stage presents a process of initializing the state for all enabled static devices. Some devices are enabled out-of-the-box by the RTOS, while others are enabled by your application configuration file (`prj.conf`) and your board configuration files as we learned in the nRF Connect SDK Fundamentals course. These latter devices encompass device driver and system driver objects that are defined using Zephyr APIs in a static manner.

    The initialization order is controlled by assigning them to specific run levels (for example, `PRE_KERNEL_1`, `PRE_KERNEL_2`), and their initialization sequence within the same run level is further defined using priority levels. Keep in mind that at this stage, the scheduler and the Kernel services are not yet available, so these initialization functions do not rely on any Kernel services. We will dive into driver initialization in Lesson 7.

    2.1. *What gets initialized in `PRE_KERNEL_1` by default in all nRF Connect SDK applications?*
    *   **Clock Control driver:** Enables support for the hardware clock controller. Used by other subsystems and for power efficiency.
    *   **A serial driver:** Can be UART(E), RTT, or other transports. Used for debugging output (e.g., boot banner) if debugging is enabled.

    2.2. *What gets initialized in `PRE_KERNEL_2` by default in all nRF Connect SDK applications?*
    *   **System Timer driver:** Usually a Real-time counter peripheral (RTC1 on nRF91/53/52, GRTC on nRF54). Used for kernel timing services (`k_sleep()`, kernel timers).

    > **Important**: The list of devices does not include all devices that get initialized in your application. The list only provides the minimal core devices needed by the RTOS. The devices and subsystems initialized will depend on your application configuration and your board configuration file.

3.  **Multithreading Preparation**
    This is where the multithreading features get initialized, including the scheduler. The RTOS will also create two threads (System threads): The RTOS **main thread**, and the **idle thread** (responsible for power management when no other threads are ready).

    During this phase, the `POST_KERNEL` services are initiated, if any exist. Once `POST_KERNEL` services are initiated, the Zephyr boot banner is printed:
    ```
    *** Booting nRF Connect SDK v2.x.x ***
    ```
    After that, the `APPLICATION` level services are initialized, if any exist. Then, all application-defined static threads (using `K_THREAD_DEFINE()`) are initiated.

    3.1. *What gets initialized in `POST_KERNEL` by default in all nRF Connect SDK applications?*
    This is where many libraries, RTOS subsystems, and services get initialized, as they require kernel services to be available. By default, the RTOS doesn't initialize anything here itself, but enabled components do. Examples:
    *   Logging module (`CONFIG_LOG` in deferred mode): Logger thread created.
    *   Bluetooth Low Energy stack (`CONFIG_BT`): Stack initialized, RX/TX threads created.
    *   System work queue (`CONFIG_SYSTEM_WORKQUEUE`): System workqueue thread initialized.

    3.2. *What gets initialized in `APPLICATION` by default in all nRF Connect SDK applications?*
    By default, some libraries get initiated here if enabled. For instance, the AT Monitor Library (`AT_MONITOR`) for nRF91 Series.

    The RTOS main thread is the currently active thread during these final initialization phases. After it’s done, it will call your `main()` function, if it exists. If no `main()` exists, the RTOS main thread terminates, and the scheduler picks the next ready thread (user-defined, subsystem, or idle). The choice depends on thread type and priority.

    > **Note**: For multi-core hardware (e.g., nRF5340), other peripherals like the mailbox (mbox) are initialized. If TF-M is used, an entropy source (e.g., `psa-rng`) is initialized.

After boot-up, several threads and interrupts are set up. Next, we compare their execution contexts.

### Thread context vs interrupt context

Interrupt and thread contexts refer to different execution environments with distinct characteristics and intended usages.

**Thread context**

*   **Execution Context:** Normal environment where application and system threads run.
*   **Triggering Event:** Threads created by application/RTOS, scheduled based on rules (type, priority).
*   **Preemption:** Can be preempted by interrupts or higher-priority threads.
*   **Duration:** Can execute longer, more complex operations.
*   **Allowed Operations:**
    *   Access full range of kernel/OS services.
    *   Execute time-consuming operations.
    *   Wait on synchronization primitives (mutexes, semaphores, events).
    *   Perform blocking I/O.
*   **Not Allowed Operations:**
    *   Direct hardware register access without proper synchronization/abstraction.
    *   (Generally) Running extremely time-critical operations (use interrupts).

**Interrupt context**

*   **Execution Context:** Environment when an interrupt handler (ISR) is running.
*   **Triggering Event:** Triggered asynchronously by hardware events (timers, signals, I/O).
*   **Preemption:** Preempts the currently running thread context.
*   **Duration:** Expected to execute **very quickly** to minimize system latency.
*   **Interrupts Nesting:** Zephyr allows nested interrupts (higher priority interrupts can preempt lower priority ISRs).
*   **Allowed Operations:**
    *   Executing time-critical operations.
    *   Access to a restricted set of kernel services (non-blocking ones).
*   **Not Allowed Operations:**
    *   **Blocking operations** (sleeping, waiting on locks/semaphores with timeouts like `K_FOREVER`).
    *   Using most kernel services meant for thread context.

---

## Thread life cycle

A thread is the basic unit of runnable code. The vast majority of firmware code will run in threads – whether it’s a user-defined thread, a thread created by the RTOS (e.g., system workqueue thread), a thread created by an RTOS subsystem (e.g., logger module), or a thread created by a library (e.g., AT Monitor library).

A thread has the following items:

*   **Thread control block:** Type `k_thread`. An instance maintained by the RTOS holding thread metadata.
*   **Stack:** Each thread has its own stack area. Size must be adequate for the thread's processing needs.
*   **Entry point function:** The body/functionality of the thread. Usually contains an infinite loop (exiting terminates the thread). Can receive optional arguments.
*   **Thread priority:** A signed integer governing the thread's scheduling importance and type (cooperative vs. preemptible).
*   **Optional thread options:** Special flags (e.g., `K_ESSENTIAL`) affecting kernel behavior regarding the thread.
*   **Optional starting delay:** Can start immediately (`K_NO_WAIT`) or after a specified delay. Can also be created inactive (`K_FOREVER`) and started later with `k_thread_start()`.

### Creating a thread

Threads are created using either the `K_THREAD_DEFINE()` macro (static, compile-time) or the `k_thread_create()` function (dynamic, run-time, requires manual stack allocation with `K_THREAD_STACK_DEFINE`).

> **Recall**: From the Fundamentals course, threads can be started immediately or with a delay. Once started, they enter the ready queue. Creating with `K_FOREVER` delay makes them inactive until `k_thread_start()` is called.

> **Definition: Ready queue**
> The queue of threads in the Ready state. The scheduler only considers threads in this queue when selecting the next thread to run.

### Thread states

If the scheduler picks a thread for execution, its state transitions to **Running**. It stays Running until:

1.  **It becomes Unready:**
    *   **Sleeping:** Calls `k_sleep()` or derivatives.
    *   **Suspended:** Another thread calls `k_thread_suspend()`.
    *   **Waiting:** Waits for an unavailable kernel object (mutex, semaphore, etc.).
2.  **It Yields or is Preempted:**
    *   **Yielding:** Calls `k_yield()` to give up the CPU voluntarily (moves to end of ready queue).
    *   **Preempted:** Scheduler switches to a higher-priority ready thread (moved to end of ready queue).
3.  **It Terminates or Aborts:**
    *   **Termination:** Exits its entry point function (usually for non-repetitive tasks).
    *   **Aborting:** Encounters a fatal error (e.g., null pointer dereference) or is aborted by itself or another thread using `k_thread_abort()`.

*(Diagram description from original text: Thread life cycle diagram)*

More details on threads can be found on the [Threads page](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/kernel/services/threads/index.html) of the nRF Connect SDK documentation.

---

## Scheduler in-depth

The scheduler has a straightforward task: it picks a thread from the queue of ready threads (the **ready queue**) as the currently active **Running** thread and hands it the CPU.

*(Diagram description from original text: Scheduler picking from ready queue)*

Deciding which thread to run is **100% deterministic**, based on rules determining thread **priority**. The scheduler doesn't consider fairness or execution history; the firmware developer must assign priorities correctly to manage CPU sharing.

### Context switch

During thread execution, CPU registers are used, and memory is accessed. The combined state (registers, stack) forms the thread's **context**.

A thread doesn't know when it will be preempted or interrupted. If preemption occurs just before an operation (e.g., subtracting R0 and R1), other running code might change R0 and R1. If the original thread resumes without its original context, the subtraction yields an incorrect result.

To prevent this, the RTOS **saves the context** of a thread when it's preempted and **restores it** before resuming execution. This save/restore process is called **context switching**.

*(Diagram description from original text: Context switching visualization)*

Context switching consumes time and power. Good firmware design aims to minimize unnecessary context switches. Context switching also occurs for interrupts.

### Thread types

*   **Preemptible threads:** (Non-negative priority) Most common for user applications. Can be preempted by the scheduler if a higher or equal priority thread becomes ready.
*   **Cooperative threads:** (Negative priority) Cannot be preempted by the scheduler. Run until they voluntarily block (sleep, wait, yield). Used for enforcing scheduler locking, often in subsystems, drivers, or performance-critical sections. Interrupts can still preempt cooperative threads, but execution *always* returns to the interrupted cooperative thread afterward.
*   **Meta-IRQ threads:** Special class of cooperative thread, **not for user applications**. Used by drivers for urgent "bottom half" processing triggered immediately after a hardware ISR. Can preempt other threads, including cooperative ones. Example: Bluetooth LE stack uses Meta-IRQ threads.

### Thread priority

Threads are assigned integer priorities. **Lower numbers have higher priority.**
*   Negative priorities (-1 to -16 by default): Cooperative threads. System work queue often runs at -1.
*   Non-negative priorities (0 to 14 by default): Preemptible threads. `main` thread usually runs at 0. `idle` thread runs at the lowest preemptible priority (15 by default). Logger thread often runs at 14.

> **Note**: Avoid using priority 15 (or `CONFIG_NUM_PREEMPT_PRIORITIES` - 1) for user threads, as it's reserved for the idle thread. The lowest recommended user priority is 14 (or `CONFIG_NUM_PREEMPT_PRIORITIES` - 2).

The number of levels is configurable (`CONFIG_NUM_PREEMPT_PRIORITIES`, `CONFIG_NUM_COOP_PRIORITIES`). Priorities can be changed dynamically at runtime (`k_thread_priority_set`), potentially changing a thread between preemptible and cooperative types.

### Scheduler locking and disabling interrupts

*   **Scheduler Locking:** Temporarily prevents context switching between threads, ensuring atomic execution of a code section relative to other threads.
    *   Cooperative threads inherently provide scheduler locking.
    *   Preemptible threads can use `k_sched_lock()` and `k_sched_unlock()`. `k_sched_lock()` effectively makes the current thread behave cooperatively while locked. (Not commonly used in application code).
*   **Disabling Interrupts:** Protects a critical section from both thread preemption *and* ISRs. Use `irq_lock()` (returns an interrupt locking key) and `irq_unlock(key)`. Use with extreme caution and for very short durations.

### Threads with equal priority

Multiple threads can share the same priority level (except the idle priority). The scheduler handles this based on configuration:

*   **Default behavior:** Runs the thread that became ready first (FIFO within the priority level).
*   **Time slicing (`CONFIG_TIMESLICING=y`):** Each thread runs for a fixed duration (`CONFIG_TIMESLICE_SIZE`) before being preempted, allowing other threads at the *same priority* to run. (Covered in Fundamentals Lesson 7, Exercise 2). Only affects priorities >= `CONFIG_TIMESLICE_PRIORITY`.
*   **Earliest Deadline First (EDF) (`CONFIG_SCHED_DEADLINE=y`):** Scheduler picks the thread with the earliest deadline (set via `k_thread_deadline_set()`). Developer is responsible for setting deadlines.

### Rescheduling points

Zephyr's tickless kernel relies on **rescheduling points** (events triggering scheduler evaluation) instead of periodic ticks. Examples:

*   `k_yield()` called.
*   Thread blocks (e.g., `k_sleep()`, waiting on semaphore/mutex).
*   A blocked thread becomes unblocked (e.g., semaphore given, data arrives in queue).
*   Time slice expires (if `CONFIG_TIMESLICING=y`).

---

## Data passing

Now that we understand execution contexts (ISRs, threads), let's learn how to safely exchange data between them. We'll cover message queues and FIFOs.

### Message queue (`k_msgq`)

A **message queue** is a thread-safe kernel object holding a fixed number of fixed-size data items (messages).

*   **Thread Safety:** Kernel manages internal locking; multiple threads can safely put/get messages.
*   **Data Type:** Message size/type defined statically at creation. Can be simple types, structs, pointers, etc.
*   **Capacity:** Fixed number of messages, defined at creation. Limited by available RAM.
*   **Blocking/Timeout:** Threads can wait (`K_FOREVER` or timeout with `K_MSEC()`) if the queue is full (when putting) or empty (when getting).
*   **Priority Handling:** If multiple threads wait, the highest-priority waiting thread is serviced first when space/data becomes available.
*   **ISR Usage:** Can be used from ISRs, but **never** with blocking waits (`K_FOREVER` or timeouts > 0). Use `K_NO_WAIT`.

*(Diagram description from original text: Message queue visualization)*

Message queues use a ring buffer internally. Data size must be a multiple of alignment (usually 4 bytes). Pad data or use compiler attributes (`__aligned(4)`) if needed.

#### How to use

1.  **Decide message data structure.** Example using a union within a struct for variable data types:
    ```c
    struct MyStruct {
      int dataType; // 0=int, 1=float, 2=string...
      union {
        int intValue;
        float floatValue;
        char stringValue[24];
      } data;
    };
    ```
    (Example from Bluetooth HRS sample uses `struct bt_hrs_client_measurement`).

2.  **Define and initialize the message queue** using `K_MSGQ_DEFINE()`:
    *(Description of image: K_MSGQ_DEFINE() parameters)*
    ```c
    // Example: Queue for 16 messages, each sizeof(uint32_t), 4-byte aligned
    K_MSGQ_DEFINE(device_message_queue, sizeof(uint32_t), 16, 4);
    ```

3.  **Write (put) a message** using `k_msgq_put()`:
    ```c
    uint32_t my_message = 123;
    int ret = k_msgq_put(&device_message_queue, &my_message, K_FOREVER); // Wait if full
    if (ret != 0) {
        // Handle error (e.g., -ENOMSG if K_NO_WAIT and full, -EAGAIN if timeout)
    }
    ```
    *   `K_FOREVER`: Wait indefinitely if full.
    *   `K_MSEC(timeout_ms)`: Wait up to `timeout_ms` if full.
    *   `K_NO_WAIT`: Return immediately (-ENOMSG) if full.

4.  **Read (get) a message** using `k_msgq_get()` (removes message) or `k_msgq_peek()` (reads without removing):
    *(Description of image: k_msgq_get() parameters)*
    ```c
    uint32_t received_message;
    int ret = k_msgq_get(&device_message_queue, &received_message, K_FOREVER); // Wait if empty
    if (ret == 0) {
        // Process received_message
    } else {
        // Handle error (e.g., -EAGAIN if timeout, -ENOMSG if K_NO_WAIT and empty)
    }
    ```
    Messages are read in FIFO order.

**Suggested Use:** Transferring fixed-size data items asynchronously between threads (and carefully with ISRs).

### FIFO (`k_fifo`)

A **FIFO** (First-In, First-Out) is a kernel object providing a queue for data items of **variable size and number**. Threads and ISRs can add/remove items.

*   **Dynamic Size/Number:** Doesn't require specifying item size or count statically.
*   **Pointer Queue:** FIFO stores *pointers* to data items, not the data itself.
*   **Memory Management:** Typically requires dynamic memory allocation (heap: `k_malloc`, `k_free`) for the data items themselves. Developer is responsible for freeing memory after consuming items.
*   **Capacity Limit:** Limited only by available heap memory (`CONFIG_HEAP_MEM_POOL_SIZE`).
*   **Blocking/Timeout:** `k_fifo_get()` can block/timeout if empty. `k_fifo_put()` does *not* block (assumes heap has space).
*   **ISR Usage:** Can be used from ISRs (non-blocking `k_fifo_put`, `k_fifo_get` with `K_NO_WAIT`).

*(Diagram description from original text: FIFO visualization using heap)*

#### How to use

1.  **Allocate heap memory** in `prj.conf`. Set based on maximum expected concurrent items and their sizes. Default is 0.
    ```kconfig
    CONFIG_HEAP_MEM_POOL_SIZE=4096 # Example: 4KB heap
    ```
    > **Note**: Handle heap allocation carefully in embedded systems. Ensure `k_free` is always called for consumed items to prevent memory leaks.

2.  **Define the FIFO** statically using `K_FIFO_DEFINE()`:
    ```c
    K_FIFO_DEFINE(my_fifo);
    ```

3.  **Define the data item structure.** The **first member MUST be `void *fifo_reserved;`** for the kernel's internal linked list.
    Example 1: Fixed-size data buffer within the item:
    ```c
    struct data_item_t {
        void *fifo_reserved; // MUST BE FIRST
        uint8_t  data[256];
        uint16_t len;
    };
    ```
    Example 2: Pointer to variable-size data allocated separately:
    ```c
    struct data_item_var_t {
        void *fifo_reserved; // MUST BE FIRST
        void *data; // Pointer to heap-allocated data
        uint16_t len;
    };
    ```

4.  **Add (put) a data item** using `k_fifo_put()`:
    *(Description of image: k_fifo_put() API)*
    ```c
    /* Allocate memory for the data item */
    struct data_item_t *buf = k_malloc(sizeof(struct data_item_t));
    if (buf == NULL) {
        /* Handle allocation failure */
        return;
    }
    /* Populate the data item (e.g., using memcpy, snprintf) */
    // buf->len = ...;
    // memcpy(buf->data, source_data, buf->len);

    /* Put the pointer into the FIFO */
    k_fifo_put(&my_fifo, buf); // Does not block
    ```
    The same item cannot be added twice without being removed first.

5.  **Read (get) a data item** using `k_fifo_get()` (removes pointer from FIFO):
    *(Description of image: k_fifo_get() API)*
    ```c
    struct data_item_t *rec_item = k_fifo_get(&my_fifo, K_FOREVER); // Wait if empty
    if (rec_item != NULL) {
        /* Process FIFO data item using rec_item->data, rec_item->len */

        /* CRITICAL: Free the allocated memory */
        k_free(rec_item);
    } else {
        // Handle error (e.g., NULL if K_NO_WAIT and empty, or other errors)
    }
    ```
    Failure to `k_free()` consumed items leads to heap overflow.

Complete FIFO API list [here](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/kernel/services/data_passing/fifos.html#api-reference).

**Suggested Use:** Asynchronously transferring variable-size or variable-number data items between threads (and carefully with ISRs), especially when dynamic allocation is acceptable.

> **Important**: You *can* use statically allocated memory pools instead of the heap with FIFOs if dynamic allocation is undesired, but managing the static pool becomes the developer's responsibility. Remember: never add the *same* data item instance twice.

---

## Exercise 1 – Exploring threads and ISRs

In this exercise, you will learn through hands-on exercises how to differentiate between thread context and interrupt context, and to understand the allowed operations in each.

The exercise covers the use of the **Kernel Timer API**. It is used to periodically trigger a function (ISR) that runs in the System timer interrupt context (RTC1 on nRF5x/nRF91, GRTC on nRF54).

You will practice collecting information about running threads using the **nRF Debug view** in VS Code:
*   Stack allocation and run-time usage.
*   Priority and state (Running, Ready, Unready).
*   Ready queue content.

You will also use a **message queue** to pass data safely between threads.

This exercise assumes you have completed Lesson 1 of the Fundamentals course and have the SDK and VS Code set up.

### Exercise steps

#### Getting the course’s repository

(Steps A-D describe adding the course repo (`devacademy-ncsinter`) to the SDK's `west.yml` manifest and running `west update`. Perform these steps once if you haven't already.)

A. Open VS Code, open the **nRF Connect terminal**.
   > **Important**: Use the nRF Connect terminal for `west` commands.
B. Type `west manifest --path` to find your `west.yml` file location. Ctrl+Click the path to open it.
C. Add the course repository to `west.yml` under `projects:`, ensuring correct indentation:
   ```yaml
     # Other third-party repositories
     - name: devacademy-ncsinter
       path: nrf/samples/devacademy/ncs-inter # Or your preferred path
       revision: main # Or specific tag/commit
       url: https://github.com/NordicDeveloperAcademy/ncs-inter
   ```
   Save the file.
D. In the nRF Connect terminal, run `west update -x devacademy-ncsinter` to download the repository. The course code will be in the specified `path`.

#### Opening the code base

(Perform for each exercise)

A. In VS Code nRF Connect extension, click **Create a new application** -> **Copy a sample**.
B. Search for the exercise name: `Lesson 1 – Exercise 1`. Select the base code version matching your SDK.
C. Choose a location to store the exercise copy (e.g., `C:\myfw\ncsinter\l1_e1`).
D. Press Enter. VS Code will copy the sample and open it.

#### Building the application

This exercise creates an application with:
*   **5 Threads:** producer (prio 6), consumer (prio 7), main (prio 0), logging (prio 14), idle (prio 15).
*   **1 Timer ISR:** Runs every 500ms in interrupt context, toggling LEDs.

*   **Main thread:** Sets up GPIO, starts timer, terminates.
*   **Producer thread:** Generates emulated sensor data (struct), puts into message queue every 2.2s. Stack 2048 bytes.
*   **Consumer thread:** Waits (`K_FOREVER`) for data on message queue, logs received data. Stack 2048 bytes.
*   **Logging/Idle threads:** System threads as described before.

#### Modifying the code

1.  **Enable debugging options** in `prj.conf`:
    ```kconfig
    # Enable thread info for debugger and optimize for debugging
    CONFIG_DEBUG_THREAD_INFO=y
    CONFIG_DEBUG_OPTIMIZATIONS=y
    ```
    > **Note**: Alternatively, use the "Optimize for debugging (-Og)" option in the VS Code build configuration GUI.

2.  **Create a kernel timer** that runs `timer0_handler` in interrupt context.
    2.1. Define the timer statically (e.g., near top of `main.c`):
    ```c
    // STEP 2.1: Define timer
    K_TIMER_DEFINE(timer0, timer0_handler, NULL); // Expiry func = timer0_handler, Stop func = NULL
    ```
    2.2. Start the timer periodically in `main()`:
    ```c
    // STEP 2.2: Start timer
    /* start periodic timer that expires once every 0.5 second */
    k_timer_start(&timer0, K_MSEC(500), K_MSEC(500)); // Initial delay 500ms, period 500ms
    ```
    2.3. Create the timer handler function (`timer0_handler`) *before* `main()`:
    ```c
    // STEP 2.3: Define timer handler function (runs in ISR context)
    static void timer0_handler(struct k_timer *dummy)
    {
        /* Interrupt Context - System Timer ISR */
        static bool flip = true;
        // Ensure led0 and led1 are defined gpio_dt_spec accessible here
        if (flip) {
            gpio_pin_toggle_dt(&led0);
        } else {
            gpio_pin_toggle_dt(&led1);
        }
        flip = !flip;
    }
    ```

3.  **Pass data using a message queue.**
    3.1. Define the message data structure (e.g., after includes):
    ```c
    // STEP 3.1: Define message structure
    typedef struct {
        uint32_t x_reading;
        uint32_t y_reading;
        uint32_t z_reading;
    } SensorReading;
    ```
    3.2. Define the message queue (e.g., near top of file):
    ```c
    // STEP 3.2: Define message queue (holds 16 SensorReading messages, 4-byte aligned)
    K_MSGQ_DEFINE(device_message_queue, sizeof(SensorReading), 16, 4);
    ```
    3.3. Write messages from the producer thread. Add inside the `producer_func`'s loop:
    ```c
    // STEP 3.3: Put message in queue (inside producer_func loop)
    // Assume 'acc_val' is a variable of type SensorReading populated with data
    ret = k_msgq_put(&device_message_queue, &acc_val, K_FOREVER); // Wait if full
    if (ret) {
        LOG_ERR("Return value from k_msgq_put = %d", ret);
    }
    ```
    3.4. Read messages in the consumer thread. Add inside the `consumer_func`'s loop:
    ```c
    // STEP 3.4: Get message from queue (inside consumer_func loop)
    SensorReading temp; // Local variable to store received message
    ret = k_msgq_get(&device_message_queue, &temp, K_FOREVER); // Wait if empty
    if (ret) {
        LOG_ERR("Return value from k_msgq_get = %d", ret);
    } else {
        // Process received message in 'temp'
        LOG_INF("Values got from the queue: %u.%u.%u", temp.x_reading, temp.y_reading, temp.z_reading);
    }
    ```

4.  **Build** your application (add build configuration if needed).

#### Debugging and analytics

Follow these steps after building:

1.  **Start a debugging session** (Actions view -> Debug button). Execution breaks at `main()`.
2.  Open the **Run and Debug View** (Activity Bar icon).
3.  Open the **Thread Viewer** (Panel View area -> nRF Debug tab).
    *   Observe the initial threads (main, producer, consumer, logging, idle), their priorities, and states. `main` is running.
    *   Use "Enable Tracking" (brush icon) next to Stack Usage to see real-time stack high water marks.

#### Threads in an nRF Connect SDK application

1.  **Set breakpoints:** Click in the gutter next to the line numbers for `k_msgq_put()` in `producer_func` and `k_msgq_get()` in `consumer_func`.
2.  **Continue execution** (F5 or Continue button). Execution stops at the breakpoint in `producer_func`.
    *   Observe in Thread Viewer: `main` is gone (terminated). `producer` is Running.
3.  **Watch the message queue:** Right-click `device_message_queue` in the code -> Add to Watch. Observe `used_msgs: 1` in the Watch view. Check stack usage.
4.  **Continue execution.** Execution stops at the breakpoint in `consumer_func`.
    *   Observe in Thread Viewer: `producer` is Unready (likely sleeping due to `k_msleep`). `consumer` is Running.
5.  **Watch the message queue:** Observe `used_msgs: 0` in the Watch view. Check stack usage updates.
6.  **Continue execution.** `consumer` blocks again on `k_msgq_get` (empty queue), becomes Unready. `logging` thread might run briefly if logs were generated, then becomes Unready. `idle` thread becomes Running (system likely enters low power).
7.  **Remove breakpoints.**
8.  **Continue execution.**
9.  **View serial output:** Switch to nRF Connect extension -> Connected Devices -> Connect to Serial Port. Observe the logged messages from the consumer thread appearing every ~2.2 seconds.

#### ISR in an nRF Connect SDK application

1.  **Add a breakpoint** inside `timer0_handler()`.
2.  **Continue execution.** Breakpoint hits periodically (every 500ms).
3.  **Examine Call Stack:** In the Run and Debug view -> CALL STACK panel, observe that `timer0_handler()` is running in an "Exception handler" context, likely interrupting the `idle` thread or another lower-priority thread.
4.  **Remove the breakpoint.**

#### Experimenting with the dos and don’ts of the interrupt context

1.  **Add a blocking call** inside `timer0_handler()` (DO NOT DO THIS IN REAL CODE):
    ```c
    static void timer0_handler(struct k_timer *dummy)
    {
        k_msleep(2000); // <<< ADD THIS (BAD!)
        // ... rest of handler code ...
    }
    ```
2.  Build the application. It will build without compile errors.
3.  Flash the application. Observe the output. The system will likely crash and continuously reset, printing fatal error messages because blocking (`k_msleep`) is illegal in an ISR context.
    ```terminal
    [timestamp] <err> os: ***** MPU FAULT *****
    ...
    [timestamp] <err> os: >>> ZEPHYR FATAL ERROR ...
    [timestamp] <err> os: Fault during interrupt handling
    ... (board resets and repeats)
    ```
    > **More on this: Build targets with TF-M**
    > If using a TF-M target (e.g., `_ns`), the fatal error might appear on the Secure Processing Environment's log output (not typically routed to the application VCOM). You might just see the application boot, print one log, reset, and repeat.

4.  **Restore the application:** Remove the `k_msleep(2000);` call, rebuild, and re-flash.

> **Important**: If lengthy processing is needed based on a timer, use the timer ISR to submit work to a **work queue** instead of performing the work directly in the ISR.

---

## Exercise 2 – Kernel options

This exercise practices using **FIFO** for data passing and explores kernel configuration options via the **nRF Kconfig GUI**.

You will build an application similar to Exercise 1, but the producer thread will generate a *random* number of data items (4-14) each time it runs, emulating variable data arrival. FIFO is suitable for this scenario.

### Exercise steps

Open the exercise base code: `l1/l1_e2` (select version) from the course repository using "Copy a sample".

1.  **Enable random number generation** in `prj.conf` for emulation:
    ```kconfig
    # STEP 1: Enable Entropy driver for random numbers
    CONFIG_ENTROPY_GENERATOR=y
    ```
    This enables the hardware entropy source. `sys_rand32_get()` can then be used.

2.  **Allocate heap size** in `prj.conf` for FIFO data items. Calculate based on max items (14) * item size (~40 bytes assumed) + overhead. 1024 bytes should be sufficient here.
    ```kconfig
    # STEP 2: Set Heap Size for FIFO items
    CONFIG_HEAP_MEM_POOL_SIZE=1024
    ```
3.  **Define the FIFO** globally in `main.c`:
    ```c
    // STEP 3: Define FIFO
    K_FIFO_DEFINE(my_fifo);
    ```
4.  **Define the FIFO data item structure** (ensure `fifo_reserved` is first):
    ```c
    // STEP 4: Define FIFO data item structure
    #define MAX_DATA_SIZE 40 // Example max size for string
    struct data_item_t {
        void *fifo_reserved; // MUST BE FIRST
        uint8_t  data[MAX_DATA_SIZE];
        uint16_t len; // Actual length of data in the buffer
    };
    ```
5.  **Add data items to the FIFO** in `producer_func()`. Replace the previous message queue logic:
    ```c
    // STEP 5: Modify producer to use FIFO
    #define MIN_DATA_ITEMS 4
    #define MAX_DATA_ITEMS 14
    static uint32_t dataitem_count = 0; // Keep track of sequence

    void producer_func(void) // Renamed for clarity
    {
        LOG_INF("Producer Thread started");
        while (1) {
            int bytes_written;
            /* Generate a random number of items to send */
            uint32_t data_number =
                MIN_DATA_ITEMS + sys_rand32_get() % (MAX_DATA_ITEMS - MIN_DATA_ITEMS + 1);

            for (int i = 0; i < data_number; i++) {
                /* Create (allocate) a data item */
                struct data_item_t *buf = k_malloc(sizeof(struct data_item_t));
                if (buf == NULL) {
                    LOG_ERR("Unable to allocate memory for FIFO item");
                    // Consider how to handle allocation failure (e.g., break, return)
                    continue; // Skip this item if allocation fails
                }
                /* Populate the data item */
                bytes_written = snprintf(buf->data, MAX_DATA_SIZE, "Data Seq. %u: %u",
                                         dataitem_count, sys_rand32_get());
                if (bytes_written < 0 || bytes_written >= MAX_DATA_SIZE) {
                     LOG_ERR("snprintf error or buffer too small");
                     // Handle error, maybe free buffer
                     k_free(buf);
                     continue;
                }
                buf->len = bytes_written;
                dataitem_count++;

                /* Put pointer to item in FIFO */
                k_fifo_put(&my_fifo, buf);
            }
            LOG_INF("Producer: Data Items Generated: %u", data_number);
            k_msleep(PRODUCER_SLEEP_TIME_MS); // Assume defined elsewhere (e.g., 2200)
        }
    }
    ```
6.  **Read data items from the FIFO** in `consumer_func()`. Replace previous message queue logic:
    ```c
    // STEP 6: Modify consumer to use FIFO
    void consumer_func(void) // Renamed for clarity
    {
        LOG_INF("Consumer Thread started");
        while (1) {
            struct data_item_t *rec_item;
            /* Get pointer to item from FIFO (waits if empty) */
            rec_item = k_fifo_get(&my_fifo, K_FOREVER);
            if (rec_item != NULL) {
                 LOG_INF("Consumer: %s\tSize: %u", rec_item->data, rec_item->len);
                 /* CRITICAL: Free the memory allocated by producer */
                 k_free(rec_item);
            }
            // No sleep needed here, k_fifo_get handles waiting
        }
    }
    ```
7.  Build and flash.
8.  Connect serial terminal and examine output. Observe variable numbers of items logged per producer cycle. Sample:
    ```terminal
    [timestamp] <inf> Less1_Exer2: Producer: Data Items Generated: 4
    [timestamp] <inf> Less1_Exer2: Consumer: Data Seq. 742:  1266499320      Size: 25
    [timestamp] <inf> Less1_Exer2: Consumer: Data Seq. 743:  4061392639      Size: 25
    [timestamp] <inf> Less1_Exer2: Consumer: Data Seq. 744:  1452774199      Size: 25
    [timestamp] <inf> Less1_Exer2: Consumer: Data Seq. 745:  721881686       Size: 24
    [timestamp] <inf> Less1_Exer2: Producer: Data Items Generated: 11
    [timestamp] <inf> Less1_Exer2: Consumer: Data Seq. 746:  1090030288      Size: 25
    ...
    ```

#### Exploring kernel options

9.  **Open the nRF Kconfig GUI.**
    > **Important**: For SDK v2.8.0+, select the application image in the APPLICATIONS view *before* opening the Kconfig GUI.
    Navigate to `Sub Systems and OS Services -> Kernel -> General Kernel Options`.

    9.1. **Examine top options:**
    *   `CONFIG_MULTITHREADING`: Enabled by default.
    *   Priority levels (`CONFIG_NUM_PREEMPT_PRIORITIES`, `CONFIG_NUM_COOP_PRIORITIES`).
    *   Scheduling algorithms (EDF, MetaIRQ enable/disable).
    *   Stack sizes (`CONFIG_MAIN_STACK_SIZE`, `CONFIG_ISR_STACK_SIZE`, `CONFIG_IDLE_STACK_SIZE`).

    9.2. **Scroll down:**
    *   **Scheduler priority queue algorithm:** Default `Simple linked-list` is good for few runnable threads.
    *   **Wait queue priority algorithm:** Default `Simple linked-list` good for few threads blocked per primitive. (Usually leave defaults).

    9.3. **Scroll down:**
    *   **Kernel Debugging and Metrics:**
        *   `CONFIG_INIT_STACKS`: Initialize stacks with 0xaa for manual high water mark checking (nRF Debug view does this automatically).
        *   `CONFIG_BOOT_BANNER`: Prints "*** Booting..." banner.
        *   `CONFIG_BOOT_DELAY`: Adds delay before application init.
        *   `CONFIG_THREAD_MONITOR`: Needed for nRF Debug thread view.
        *   `CONFIG_THREAD_NAME`: Allows naming threads. (Both enabled by `CONFIG_DEBUG_THREAD_INFO`).
        *   `CONFIG_THREAD_RUNTIME_STATS`: Collects stats (not used here).
    *   **Work Queue Options:**
        *   `CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE`: Stack size for system workqueue thread.
        *   `CONFIG_SYSTEM_WORKQUEUE_PRIORITY`: Priority of system workqueue thread (default -1, cooperative).
        *   `CONFIG_SYSTEM_WORKQUEUE_NO_YIELD`: Disable yielding between system work items (use with caution).

    9.4. **Scroll down:**
    *   **Timer API Options:**
        *   `CONFIG_TIMESLICING` options (covered before).
        *   `CONFIG_POOL`: Enables Polling API (`k_poll`).
    *   **Other Kernel Object Options:**
        *   `CONFIG_EVENTS`: Enable `k_event` objects.
        *   `CONFIG_HEAP_MEM_POOL_SIZE`: Heap size (configured earlier).

    9.5. **Scroll down (End):**
    *   System clock frequencies (`CONFIG_SYS_CLOCK_TICKS_PER_SEC`, `CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC`) - usually architecture defaults.
    *   **Security:** `CONFIG_STACK_CANARIES` (adds runtime stack overflow checks, impacts performance/size, good for debugging).
    *   `CONFIG_TICKLESS_KERNEL`: Enabled by default.

### Summary Table

This table summarizes the execution primitives discussed:

| Primitive          | Features                                                                                                | Intended Use                                                                  | Level of Determinism | Example Usage                                                                                                 |
| :----------------- | :------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------ |
| Preemptible thread | Isolated unit, own stack.                                                                               | Application code.                                                             | High                 | Most examples in this course, Logger deferred thread.                                                         |
| Cooperative thread | Can't be preempted by threads*. Enforces scheduler locking.                                             | Subsystems, network stacks, drivers, performance-critical app code.           | High                 | System workqueue, MPSL timeslot sample, BT HCI drivers.                                                       |
| System workqueue   | Lightweight (shared stack). Kernel-created. FIFO order. Yields between items (default).                 | Subsystems, drivers, Deferring ISR work, lightweight non-blocking app code.   | Moderate             | BT stack, MCUmgr, Deferring in bh1749 driver, Central HID sample.                                             |
| User workqueue     | Lightweight (shared stack). User-created. Not shared with subsystems (more deterministic than system q). | Application code, Subsystems creating private queues, Deferring ISR work.     | Above moderate       | Fundamentals L7E3, Wi-Fi Provisioning sample, MQTT sample, Network TCP stack.                               |
| Meta-IRQ           | Special cooperative thread. Can preempt even cooperative threads*.                                      | Driver "bottom half" urgent work.                                             | Very high            | Bluetooth LE stack Link Layer.                                                                                |
| Regular ISR        | Asynchronous hardware trigger.                                                                          | Device drivers, High-determinism non-blocking app code.                       | Extremely high       | Most drivers (e.g., nRF700X Wi-Fi).                                                                         |
| Direct ISR         | Asynchronous, lower overhead/latency than regular ISR, reduced kernel feature access.                   | Low-latency drivers.                                                          | Highest              | Special drivers (timers, radios), BT LE Link Layer Controller.                                                |

*\*Meta-IRQ threads can preempt cooperative threads, but execution returns to the interrupted cooperative thread afterward.*