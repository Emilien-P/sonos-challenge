import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.CountDownLatch;

import javax.swing.SwingUtilities;

import javafx.embed.swing.JFXPanel;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;

/**
 * Socket connection with localhost on port 8080
 * expects messages of the format name/google_speech_output
 * 
 * Currently supports:
 * 	- play my playlist (expecting "my playlist" as google speech output)
 * 	- play something I like (expecting "something I like" as google speech output)
 *  - I like *genre* (expecting "I like name_of_genre")
 *  
 *
 *	Experiment workflow:
 *	- Do the calibration (Emilien command line) for Ege, Emilien, Alvin
 *	- Do a guess
 *		--> fetch result of model (name)
 *		--> fetch result of google_speech_api (google_speech_output)
 *		----> send via socket name/google_speech_output
 *			  and this program takes care of the rest
 *	
 *	TODO: So when doing the guess, your python script should connect to the socket as a client
 *	and send through the buffer {name/google_speech_output}. 
 *
 *	I have attached a very basic template of how to connect to the socket in "pythonToJavaSocketTemplate.py"
 *	check that out and just implement a similar thing to your side of the code.
 *
 */

public class Main {
	static String fromClient;
    static String toClient;
    
	public static void main(String[] args) throws InterruptedException, IOException {
		final CountDownLatch latch = new CountDownLatch(1);
		SwingUtilities.invokeLater(new Runnable() {
		    public void run() {
		        new JFXPanel(); // initializes JavaFX environment
		        latch.countDown();
		    }
		});
		latch.await();
		
		List<String> g = new ArrayList<>();
		User ege = new User(0, "Ege", g);
		User alvin = new User(1, "Alvin", g);
		User emilien = new User(2, "Emilien", g);
		
		SonosModel sonos = new SonosModel(Arrays.asList(ege, emilien, alvin));
		
		ServerSocket server = new ServerSocket(8080);
        System.out.println("wait for connection on port 8080");
        
        boolean run = true;
        Socket client = server.accept();
		System.out.println("got connection on port 8080");
		BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
		PrintWriter out = new PrintWriter(client.getOutputStream(),true);
        while(run) {
      
        		fromClient = in.readLine();
        		System.out.println("received: " + fromClient);
        		
        		if(fromClient.startsWith("Ege") || fromClient.startsWith("Alvin") || fromClient.startsWith("Emilien")) {
        			String[] tokens = fromClient.split("/");
        			
        			if(tokens[1].toLowerCase().equals("my playlist")) {
        				sonos.stopPlaying();
        				sonos.startPlaylist(tokens[0]);
        			}else if(tokens[1].equals("something I like")){
        				sonos.stopPlaying();
        				sonos.startTaste(tokens[0]);
        			}else if(tokens[1].startsWith("I like")) {
        				String genre = tokens[1].split(" ")[2];
        				sonos.getUser(tokens[0]).addGenre(genre);
        			}else {
        				System.out.println("Bad parameter");
        			}
        		}
        		else if(fromClient.startsWith("quit")) {
        			out.close();
        			run = false;
        			server.close();
        		}else {
        			System.out.println("Bad parameter");
        		}
        }
        System.exit(0);
	}
}
