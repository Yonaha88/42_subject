/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strtrim.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/26 17:49:50 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:20:40 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	is_in_set(char c, char const *set)
{
	size_t	idx;

	idx = 0;
	while (set[idx])
	{
		if (c == set[idx])
			return (1);
		idx++;
	}
	return (0);
}

char	*ft_strtrim(char const *src, char const *set)
{
	size_t	start;
	size_t	end;
	size_t	trim_len;
	char	*trim;

	if (src == NULL)
		return (NULL);
	if (set == NULL)
		return (ft_strdup(src));
	start = 0;
	while (src[start] && is_in_set(src[start], set))
		start++;
	end = ft_strlen(src);
	while (end > start && is_in_set(src[end - 1], set))
		end--;
	trim_len = end - start;
	trim = (char *)malloc((trim_len + 1) * sizeof(char));
	if (trim == NULL)
		return (NULL);
	ft_strlcpy(trim, src + start, trim_len + 1);
	return (trim);
}
