import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.FlowLayout;
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

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JTextArea;
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

public class Main extends JFrame  {
	private final static int NUM_CALIBRATE = 15;
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
		
		SonosFrame sf = new SonosFrame();
		
		
		JTextArea ta = new JTextArea(1,20);
		JPanel northPanel = new JPanel();
		//northPanel.setLayout(new BoxLayout(northPanel,BoxLayout.Y_AXIS));
		JPanel p2 = new JPanel();
		
		p2.setBackground(Color.DARK_GRAY);
		
		ta.append("test");
		JButton egeButton = new JButton("Calibrate Ege");
		JButton emilienButton = new JButton("Calibrate Emilien");
		JButton alvinButton = new JButton("Calibrate Alvin");
		JButton record = new JButton("Record command");
		JButton init = new JButton("Initialize");
		
		
		JComboBox initModel = new JComboBox();
		initModel.addItem("linear support vector machine (default)");
		initModel.addItem("sequential neural network");
		initModel.addItem("convolutional neural network");
		initModel.addItem("long short-term memory neural network");
		
		JComboBox initBootstrap = new JComboBox();
		initBootstrap.addItem("No Bootstrap");
		initBootstrap.addItem("Bootstrap");
		
		List<String> models = Arrays.asList("linSVM", "seqNN", "CNN", "LSTM");
		
		p2.add(initModel);
		p2.add(initBootstrap);
		p2.add(init);
		
		northPanel.add(p2);
		//northPanel.add(p1);
		sf.add(p2, BorderLayout.NORTH);
		sf.add(record, BorderLayout.SOUTH);
		sf.add(ta, BorderLayout.CENTER);
		
		ServerSocket server = new ServerSocket(8080);
        System.out.println("wait for connection on port 8080");
        
        boolean run = true;
        Socket client = server.accept();
		System.out.println("got connection on port 8080");
		BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
		PrintWriter out = new PrintWriter(client.getOutputStream(),true);
		
		init.addActionListener(e -> {
			out.println("initialize " + models.get(initModel.getSelectedIndex()) + " " + initBootstrap.getSelectedIndex());
			JPanel p1 = new JPanel();
			p1.setBackground(Color.BLACK);
			p1.add(egeButton);
			p1.add(emilienButton);
			p1.add(alvinButton);
			
			sf.remove(p2);
			sf.add(p1, BorderLayout.NORTH);
			sf.revalidate();
			sf.repaint();
		});
		
		egeButton.addActionListener(e -> out.println("calibrate Ege " + NUM_CALIBRATE + " 1"));
		emilienButton.addActionListener(e -> out.println("calibrate Emilien " + NUM_CALIBRATE + " 1"));
		alvinButton.addActionListener(e -> out.println("calibrate Alvin " + NUM_CALIBRATE + " 1"));
		record.addActionListener(e -> {
			sonos.stopPlaying();
			ta.setText("Listening for a command");
			out.println("listen");
		});
		
        while(run) {
        		
        		fromClient = in.readLine();
        		System.out.println("received: " + fromClient);
        		
        		if(fromClient.startsWith("Ege") || fromClient.startsWith("Alvin") || fromClient.startsWith("Emilien")) {
        			String[] tokens = fromClient.split("/");
        			String googleSays = "Okay " + tokens[0] + ".";
        			
        			if(tokens[1].toLowerCase().contains("my playlist")) {
        				googleSays += " playing your playlist";
        				ta.setText("playing from " + tokens[0] + "'s playlist");
        				sonos.stopPlaying();
        			
        				sonos.startPlaylist(tokens[0]);
        				
        			}else if(tokens[1].contains("something I like")){
        				googleSays += " Playing something you like";
        				ta.setText("playing something " + tokens[0] + " likes\n");
        				ta.append(tokens[0] + " likes:\n");
        				for(String genre : sonos.getUser(tokens[0]).getGenres()) {
        					ta.append(genre + "\n");
        				}
        				sonos.stopPlaying();
        				Runtime.getRuntime().exec("/Users/ege/eclipse-workspace/Sonos_Project/src/googlespeech.sh " + EncodingUtil.encodeURIComponent(googleSays));
        				sonos.startCustom("/Users/ege/eclipse-workspace/Sonos_Project/src/playlists/googletest.mp3");
        				Thread.sleep(2500);
        				sonos.startTaste(tokens[0]);
        			}else if(tokens[1].contains("I like")) {
        				int i = tokens[1].indexOf("like");
        				
        				String genre = tokens[1].substring(i + 5).toLowerCase();
        				googleSays = "Got it, " + tokens[0] + ". I added " + genre + " to your list of tastes";
        				sonos.getUser(tokens[0]).addGenre(genre.replaceAll(" ", "_"));
        				ta.setText("(updated) " + tokens[0] + " likes:\n");
        				for(String gen : sonos.getUser(tokens[0]).getGenres()) {
        					ta.append(gen + "\n");
        				}
        				Runtime.getRuntime().exec("/Users/ege/eclipse-workspace/Sonos_Project/src/googlespeech.sh " + EncodingUtil.encodeURIComponent(googleSays));
        				sonos.startCustom("/Users/ege/eclipse-workspace/Sonos_Project/src/playlists/googletest.mp3");
        			}else if(tokens[1].contains("alarm")) {
        				int i = tokens[1].indexOf("a.m.");
        				if(i != -1) {
        					String time  = tokens[1].substring(i-2, i+4);
            				googleSays += "The Sonos in your room will wake you up at " + time;
            				Runtime.getRuntime().exec("/Users/ege/eclipse-workspace/Sonos_Project/src/googlespeech.sh " + EncodingUtil.encodeURIComponent(googleSays));
            				sonos.startCustom("/Users/ege/eclipse-workspace/Sonos_Project/src/playlists/googletest.mp3");
        				}	
        			} else {
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
