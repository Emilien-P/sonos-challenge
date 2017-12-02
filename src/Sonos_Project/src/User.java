import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class User {
	private int userId;
	private String username;
	private List<String> favoriteGenres;
	
	public User(int userId, String username, List<String> favoriteGenres) {
		this.userId = userId;
		this.username = username;
		this.favoriteGenres = new ArrayList<>(favoriteGenres);
	}
	
	public void addGenre(String g) {
		if(g.equals("chill_pop")) {
			favoriteGenres.add("POP");
		}
		else {
			favoriteGenres.add(g.toUpperCase());
		}
	}
	public int getId() {
		return userId;
	}
	public String getUsername() {
		return username;
	}
	
	public List<String> getGenres(){
		return new ArrayList<>(favoriteGenres);
	}
}
