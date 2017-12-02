import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

import javafx.animation.KeyFrame;
import javafx.animation.KeyValue;
import javafx.animation.Timeline;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import javafx.util.Duration;

public class SonosModel {
	private boolean isPlaying;
	private HashMap<String, User> users;
	private HashMap<String, String> userPlaylists;
	private final String path = "src/playlists/";
	private MediaPlayer mediaPlayer;
	
	public SonosModel(List<User> users) {
		this.users = new HashMap<>();
		isPlaying = false;
		userPlaylists = new HashMap<>();
		
		for(User user : users) {
			this.users.put(user.getUsername(), user);
			userPlaylists.put(user.getUsername(), path + user.getUsername() + "Playlist");
		}
	}
	
	public void startPlaylist(String username) throws InterruptedException, IOException {
		if(username == null || username.isEmpty() || !userPlaylists.containsKey(username)) {
			throw new IllegalArgumentException("The username must be part of the list of users!");
		}
		if(username.equals("Alvin")) {
			String x = "Okay Alvin. Playing your playlist";
			Runtime.getRuntime().exec("/Users/ege/eclipse-workspace/Sonos_Project/src/googlespeech.sh " + EncodingUtil.encodeURIComponent(x));
			Thread.sleep(500);
			Media hitz = new Media(new File("/Users/ege/eclipse-workspace/Sonos_Project/src/playlists/googletest.mp3").toURI().toString());
			mediaPlayer = new MediaPlayer(hitz);
			mediaPlayer.play();
			Thread.sleep(3000);
		}
		String playlist = userPlaylists.get(username);
		String track = playlist + "/soundsample.mp3";
		Media hit2 = new Media(new File(track).toURI().toString());

		mediaPlayer = new MediaPlayer(hit2);
		mediaPlayer.play();
		isPlaying  = true;
	}
	
	public void startCustom(String mp3filename) throws InterruptedException {
		Thread.sleep(1000);
		Media hit = new Media(new File(mp3filename).toURI().toString());
		
		mediaPlayer = new MediaPlayer(hit);
		mediaPlayer.play();
		isPlaying = true;
	}
	
	public void startTaste(String username) {
		if(username == null || username.isEmpty() || !userPlaylists.containsKey(username)) {
			throw new IllegalArgumentException("The username must be part of the list of users!");
		}
		
		User user = users.get(username);
		List<String> genres = user.getGenres();
		if(!genres.isEmpty()) {
			Collections.shuffle(genres);
			String randomFavoriteGenre = genres.get(0);
			
			String track = path + "Genres/" + randomFavoriteGenre + ".mp3";
			Media hit = new Media(new File(track).toURI().toString());
			
			mediaPlayer = new MediaPlayer(hit);
			mediaPlayer.play();
			isPlaying = true;
		}
	}
	
	public void stopPlaying() {
		if(isPlaying) {
			Timeline timeline = new Timeline(
				    new KeyFrame(Duration.seconds(1),
				        new KeyValue(mediaPlayer.volumeProperty(), 0)));
			timeline.play();
			//mediaPlayer.stop();
			isPlaying = false;
		}
	}
	
	public User getUser(String username) {
		return users.get(username);
	}
	
	public Set<String> getUsernames(){
		return users.keySet();
	}
	
}
