from sweep_line import *
import time
import matplotlib.pyplot as plt

if __name__=='__main__':
    fi_times = []
    naive_times = []

    sizes = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    num_inters_naive = []
    num_inters_fi = []
    for size in sizes:
        sweep_line = SweepLine()
        sweep_line.comparator.set_last(Point(0,0))
        segs = generate_random_segments(size)

        start = time.time()
        naive_inters = naive_seg_inter(segs)
        naive_times.append(time.time()-start)

        start = time.time()
        good_inters = sweep_line.find_intersections(segs)
        fi_times.append(time.time()-start)

        num_inters_naive.append(len(naive_inters))
        num_inters_fi.append(len(good_inters))


    print(num_inters_naive)
    print(num_inters_fi)
    print("---------------------------")

    print("NAIVE_TIMES: ", naive_times)

    plt.scatter(sizes, naive_times)
    plt.plot(sizes, naive_times)
    plt.xlabel("size, n")
    plt.ylabel("naive_seg_inter runtime / s")
    plt.show()

    print("FI_TIMES: ", fi_times)

    plt.scatter(sizes, fi_times)
    plt.plot(sizes, fi_times)
    plt.xlabel("size, n")
    plt.ylabel("find_intersection runtime / s")
    plt.show()

    plt.scatter(sizes, num_inters_fi)
    plt.plot(sizes, num_inters_fi)
    plt.xlabel("size, n")
    plt.ylabel("number of intersections")
    plt.show()

