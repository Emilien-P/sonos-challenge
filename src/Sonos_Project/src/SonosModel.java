import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;

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
	
	public void startPlaylist(String username) {
		if(username == null || username.isEmpty() || !userPlaylists.containsKey(username)) {
			throw new IllegalArgumentException("The username must be part of the list of users!");
		}
		String playlist = userPlaylists.get(username);
		String track = playlist + "/soundsample.mp3";
		Media hit = new Media(new File(track).toURI().toString());
		
		mediaPlayer = new MediaPlayer(hit);
		mediaPlayer.play();
		isPlaying  = true;
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
			mediaPlayer.stop();
			isPlaying = false;
		}
	}
	
	public User getUser(String username) {
		return users.get(username);
	}
	
}
