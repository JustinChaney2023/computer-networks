package org.example;

import com.hazelcast.cluster.Member;
import com.hazelcast.config.Config;
import com.hazelcast.core.Hazelcast;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.map.IMap;
import com.hazelcast.map.listener.EntryAddedListener;
import com.hazelcast.map.listener.EntryRemovedListener;
import com.hazelcast.map.listener.EntryUpdatedListener;

import java.util.Set;
import java.util.concurrent.TimeUnit;

public class HelloWorld {

    public static void main(String[] args) throws Exception {
        // Usage examples (run these in separate terminals):
        // mvn -q -Dexec.mainClass=org.example.HelloWorld -Dexec.args="A" exec:java
        // mvn -q -Dexec.mainClass=org.example.HelloWorld -Dexec.args="B" exec:java
        // mvn -q -Dexec.mainClass=org.example.HelloWorld -Dexec.args="C mutator" exec:java

        String node = args.length >= 1 ? args[0] : "Node";
        boolean mutator = args.length >= 2 && "mutator".equalsIgnoreCase(args[1]);

        // Start ONE embedded Hazelcast member in THIS process
        Config cfg = new Config();
        cfg.setClusterName("hello-world");      // all processes must match
        cfg.getJetConfig().setEnabled(false);   // not needed here
        HazelcastInstance hz = Hazelcast.newHazelcastInstance(cfg);

        // Show cluster membership (good for screenshots)
        System.out.println("[" + node + "] Started. Cluster members:");
        Set<Member> members = hz.getCluster().getMembers();
        for (Member m : members) {
            System.out.println("[" + node + "] -> " + m.getAddress());
        }

        // Distributed Object (required): a cluster-wide map
        IMap<String, String> map = hz.getMap("my-distributed-map"); // <- as required

        // Print in ALL instances whenever anything changes
        map.addEntryListener((EntryAddedListener<String, String>) e ->
                System.out.printf("[%s] ADDED   key=%s, val=%s, by=%s%n",
                        node, e.getKey(), e.getValue(), e.getMember().getAddress()), true);

        map.addEntryListener((EntryUpdatedListener<String, String>) e ->
                System.out.printf("[%s] UPDATED key=%s, old=%s, new=%s, by=%s%n",
                        node, e.getKey(), e.getOldValue(), e.getValue(), e.getMember().getAddress()), true);

        map.addEntryListener((EntryRemovedListener<String, String>) e ->
                System.out.printf("[%s] REMOVED key=%s, old=%s, by=%s%n",
                        node, e.getKey(), e.getOldValue(), e.getMember().getAddress()), true);

        // Only the "mutator" instance will add/update/delete; others just observe and print
        if (mutator) {
            // Small delay so watchers attach listeners first
            TimeUnit.SECONDS.sleep(2);

            System.out.println("[" + node + "] Performing mutations...");
            map.put("1", "John");           TimeUnit.SECONDS.sleep(1); // add
            map.put("2", "Mary");           TimeUnit.SECONDS.sleep(1); // add
            map.put("1", "Johnny");         TimeUnit.SECONDS.sleep(1); // update
            map.remove("2");                TimeUnit.SECONDS.sleep(1); // delete
            map.putIfAbsent("3", "Jane");   TimeUnit.SECONDS.sleep(1); // add
            map.put("3", "Janet");          TimeUnit.SECONDS.sleep(1); // update
            map.remove("1");                                       // delete
            System.out.println("[" + node + "] Done mutating.");
        }

        System.out.println("[" + node + "] Running. Ctrl+C to exit.");
        Thread.currentThread().join();
    }
}
